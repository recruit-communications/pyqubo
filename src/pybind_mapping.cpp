#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h> // vector用
#include <pybind11/numpy.h>
#include <express.h>
#include <poly.h>
#include <model.h>
#include <placeholderpoly.h>
#include <binary_quadratic_model.hpp>
#include <expanded.h>
#include <decoded_solution.h>
#include <pybase.h>


using namespace std;

PYBIND11_DECLARE_HOLDER_TYPE(T, std::shared_ptr<T>, true);

namespace py = pybind11;
using namespace pybind11::literals;


Vartype parse_vartype(string string_vartype){
    Vartype vartype;
    if(string_vartype == "BINARY"){
        vartype = Vartype::BINARY;
    }else if(string_vartype == "SPIN"){
        vartype = Vartype::SPIN;
    }else{
        throw std::invalid_argument("Invalid vartype.");
    }
    return vartype;
}

namespace pybind_model{
    py::object to_qubo(Model model, bool index_label, py::dict feed_dict){
        if(index_label){
            auto result = model.to_qubo_with_index(feed_dict.cast<FeedDict>());
            return py::cast(result);
        }else{
            auto result = model.to_qubo(feed_dict.cast<FeedDict>());
            return py::cast(result);
        }
    }

    py::object to_ising(Model model, bool index_label, py::dict feed_dict){
        if(index_label){
            auto result = model.to_ising_with_index(feed_dict.cast<FeedDict>());
            return py::cast(result);
        }else{
            auto result = model.to_ising(feed_dict.cast<FeedDict>());
            return py::cast(result);
        }
    }

    py::object to_bqm(Model model, bool index_label, py::dict feed_dict){
        py::module dimod = py::module::import("dimod");
        auto BQM = dimod.attr("BinaryQuadraticModel");

        if(index_label){
            auto qubo = model.to_qubo_with_index(feed_dict.cast<FeedDict>());
            auto q = py::cast(std::get<0>(qubo));
            double offset = std::get<1>(qubo);
            return BQM.attr("from_qubo")(q, offset);
        }else{
            auto qubo = model.to_qubo(feed_dict.cast<FeedDict>());
            auto q = py::cast(std::get<0>(qubo));
            double offset = std::get<1>(qubo);
            return BQM.attr("from_qubo")(q, offset);
        }
    }

    template <class T>
    py::object decode_sampleset_inner(Model model, py::object const sampleset, py::dict feed_dict, vector<T> variables){
        // sort samples by energy
        sampleset.attr("record").attr("sort")("order"_a="energy");
        
        auto array = sampleset.attr("record")["sample"].cast<py::array_t<int8_t>>();
        py::buffer_info info = array.request();
        if (info.format != py::format_descriptor<int8_t>::format() || info.ndim != 2)
                throw std::runtime_error("Incompatible buffer format!");
        int n_rows = info.shape[0];
        int n_cols = info.shape[1];

        vector<Sample<T>> samples;
        samples.reserve(n_rows);
        for(int i=0; i < n_rows; i++){
            Sample<T> sample;
            for(int j=0; j < n_cols; j++){
                sample[variables[j]] = *(array.data(i, j));
            }
            samples.push_back(sample);
        }
        string vartype = sampleset.attr("vartype").attr("name").cast<std::string>();
        auto map_feed_dict = feed_dict.cast<FeedDict>();
        auto decoded_sample = model.decode_samples_general<T>(samples, parse_vartype(vartype), map_feed_dict);
        return py::cast(decoded_sample);
    }

    py::object decode_sampleset(Model model, py::object const sampleset, py::dict feed_dict){
        
        // depending on the type of the label, determine the decode_sampleset function
        try{
            vector<string> variables = sampleset.attr("variables").cast<vector<string>>();
            return decode_sampleset_inner(model, sampleset, feed_dict, variables);
        }catch(...){}

        try{
            vector<uint32_t> variables = sampleset.attr("variables").cast<vector<uint32_t>>();
            return decode_sampleset_inner(model, sampleset, feed_dict, variables);
        }catch(...){}
    }

    double energy(Model model, py::dict py_sample, string py_vartype, py::dict feed_dict){
        Vartype vartype = parse_vartype(py_vartype);
        auto sample = py_sample.cast<Sample<std::string>>();
        auto map_feed_dict = feed_dict.cast<FeedDict>();
        return model.energy(sample, vartype, map_feed_dict);
    }

    py::object decode_sample_dict(Model model, py::dict py_sample, string py_vartype, py::dict feed_dict){
        
        // todo: need to validate if py_sample constains float value
        int input_size = py_sample.attr("__len__")().cast<int>();
        int model_size = model.variables().size();
        if(input_size != model_size){
            throw py::value_error("input sample size is different from the size of Model.variables()");
        }
        
        Vartype vartype = parse_vartype(py_vartype);
        auto map_feed_dict = feed_dict.cast<FeedDict>();
        try{
            auto sample = py_sample.cast<Sample<std::string>>();
            auto sol = model.decode_sample(sample, vartype, map_feed_dict);
            return py::cast(sol);
        }catch(const std::invalid_argument& e){
            //cout << "error" << e.what() << endl;
            throw e;
        }catch(...){}
        
        try{
            auto sample = py_sample.cast<Sample<uint32_t>>();
            auto sol = model.decode_sample_with_index(sample, vartype, map_feed_dict);
            return py::cast(sol);
        }catch(const std::out_of_range& e){
            //cout << "error" << e.what() << endl;
            throw e;
        }catch(...){}
    }

    py::object decode_sample_list(Model model, py::list py_sample, string py_vartype, py::dict feed_dict){
        int input_size = py_sample.attr("__len__")().cast<int>();
        int model_size = model.variables().size();
        if(input_size != model_size){
            throw py::value_error("input sample size is different from the size of Model.variables()");
        }
        // todo: need to validate if py_sample constains float value
        Vartype vartype = parse_vartype(py_vartype);
        auto sample = py_sample.cast<vector<int32_t>>();
        auto map_feed_dict = feed_dict.cast<std::map<string, double>>();
        auto sol = model.decode_sample_vector(sample, vartype, map_feed_dict);
        return py::cast(sol);
    }
}

namespace pybind_decoded_solution{
    int32_t array_value_tuple(DecodedSolution dec_sol, string array_name, py::tuple indices){
        vector<uint32_t> indices_vector = indices.cast<vector<uint32_t>>();
        string key_string = array_name;
        for(uint32_t index: indices_vector){
            key_string += "[" + std::to_string(index) + "]";
        }
        auto result = dec_sol.sample.find(key_string);
        if(result != dec_sol.sample.end()){
            return result->second;
        }else{
            throw py::key_error("provided key was not found in the array");
        }
    }

    int32_t array_value_int(DecodedSolution dec_sol, string array_name, int index){
        string key_string = array_name + "[" + std::to_string(index) + "]";
        auto result = dec_sol.sample.find(key_string);
        if(result != dec_sol.sample.end()){
            return result->second;
        }else{
            throw py::key_error("provided key was not found in the array");
        }
    }
}


PYBIND11_MODULE(cpp_pyqubo, m) {
    m.doc() = "pyqubo C++ binding";
    
    py::class_<DecodedSubH>(m, "DecodedSubH")
        .def("__repr__", &DecodedSubH::to_string)
        .def_readwrite("label", &DecodedSubH::label)
        .def_readwrite("energy", &DecodedSubH::energy);

    py::class_<DecodedSolution>(m, "DecodedSample")
        .def("__repr__", &DecodedSolution::to_string)
        .def_readwrite("sample", &DecodedSolution::sample)
        .def_readwrite("energy", &DecodedSolution::energy)
        .def_readwrite("subh", &DecodedSolution::subh_values)
        .def("array", pybind_decoded_solution::array_value_int, py::arg("array_name"), py::arg("index"))
        .def("array", pybind_decoded_solution::array_value_tuple, py::arg("array_name"), py::arg("index"))
        .def("constraints", &DecodedSolution::get_constraints, py::arg("only_broken")=false);

    py::class_<Model>(m, "Model")
        .def("__repr__", &Model::to_string)
        .def("to_qubo", pybind_model::to_qubo, py::arg("index_label")=false, py::arg("feed_dict")=py::dict())
        .def("to_ising", pybind_model::to_ising, py::arg("index_label")=false, py::arg("feed_dict")=py::dict())
        .def("to_bqm", pybind_model::to_bqm, py::arg("index_label")=false, py::arg("feed_dict")=py::dict())
        .def("decode_sample", pybind_model::decode_sample_dict, py::arg("sample"), py::arg("vartype"), py::arg("feed_dict")=py::dict())
        .def("decode_sample", pybind_model::decode_sample_list, py::arg("sample"), py::arg("vartype"), py::arg("feed_dict")=py::dict())
        .def("decode_sampleset", pybind_model::decode_sampleset, py::arg("sampleset"), py::arg("feed_dict")=py::dict())
        .def("energy", pybind_model::energy, py::arg("sample"), py::arg("vartype"), py::arg("feed_dict")=py::dict())
        .def_property_readonly("variables", &Model::variables);
    
    
    py::class_<Base, BasePtr, PyBase>(m, "Base")
        .def(py::init<>())
        .def("__add__", (BasePtr (Base::*)(BasePtr)) &Base::add)
        .def("__add__", (BasePtr (Base::*)(double)) &Base::add)
        .def("__radd__", (BasePtr (Base::*)(double)) &Base::add)
        .def("__sub__", (BasePtr (Base::*)(BasePtr)) &Base::sub)
        .def("__sub__", (BasePtr (Base::*)(double)) &Base::sub)
        .def("__rsub__", (BasePtr (Base::*)(double)) &Base::rsub)
        .def("__mul__", (BasePtr (Base::*)(BasePtr)) &Base::mul)
        .def("__mul__", (BasePtr (Base::*)(double)) &Base::mul)
        .def("__rmul__", (BasePtr (Base::*)(double)) &Base::mul)
        .def("__truediv__", (BasePtr (Base::*)(double)) &Base::div)
        .def("__pow__", &Base::pow)
        .def("__neg__", &Base::neg)
        .def("__eq__", &Base::equal_to)
        .def("__hash__", &Base::hash)
        .def("__repr__", [](BasePtr base){ return base->to_string(true);})
        .def("__str__", [](BasePtr base){ return base->to_string(true);})
        .def("compile", (Model (Base::*)(double)) &Base::compile, py::arg("strength")=5.0)
        .def("compile", (Model (Base::*)(string)) &Base::compile, py::arg("strength"));
    
    py::class_<Binary, shared_ptr<Binary>, Base>(m, "Binary")
        .def(py::init<const std::string>(),
            py::arg("label"))
        .def_readwrite("label", &Binary::label);
    
    py::class_<Spin, shared_ptr<Spin>, Base>(m, "Spin")
        .def(py::init<const std::string>(),
            py::arg("label"))
        .def_readwrite("label", &Spin::label);

    py::class_<Num, shared_ptr<Num>, Base>(m, "Num")
        .def(py::init<double>())
        .def_readwrite("value", &Num::value);
    
    py::class_<Placeholder, shared_ptr<Placeholder>, Base>(m, "Placeholder")
        .def(py::init<const std::string>(), py::arg("label"))
        .def_readwrite("label", &Placeholder::label);

    py::class_<Add, shared_ptr<Add>, Base>(m, "Add")
        .def(py::init<shared_ptr<Add>, BasePtr>())
        .def(py::init<BasePtr, BasePtr>())
        .def(py::init<BasePtr, double>())
        .def(py::init<double, BasePtr>())
        .def("__add__", (BasePtr (Add::*)(BasePtr)) &Add::add)
        .def("__add__", (BasePtr (Base::*)(double)) &Base::add);

    py::class_<Mul, shared_ptr<Mul>, Base>(m, "Mul")
        .def(py::init<BasePtr, BasePtr>())
        .def_readwrite("left", &Mul::left)
        .def_readwrite("right", &Mul::right);

    py::class_<WithPenalty, shared_ptr<WithPenalty>, Base>(m, "WithPenalty")
        .def(py::init<BasePtr, BasePtr, string>(), py::arg("express"), py::arg("penalty"), py::arg("label"))
        .def_readwrite("express", &WithPenalty::hamiltonian)
        .def_readwrite("penalty", &WithPenalty::penalty);
    
    py::class_<UserDefinedExpress, shared_ptr<UserDefinedExpress>, Base>(m, "UserDefinedExpress")
        .def(py::init<BasePtr>(), py::arg("hamiltonian"))
        .def_readwrite("hamiltonian", &UserDefinedExpress::hamiltonian);

    py::class_<SubH, shared_ptr<SubH>, Base>(m, "SubH")
        .def(py::init<BasePtr, string>(), py::arg("hamiltonian"), py::arg("label"))
        .def_readwrite("hamiltonian", &SubH::hamiltonian);
    
    py::class_<Constraint, shared_ptr<Constraint>, Base>(m, "Constraint")
        .def(py::init<BasePtr, string, std::function<bool(double)>>(),
            py::arg("hamiltonian"), py::arg("label"),
            py::arg("condition")=py::cpp_function([](double x){ return x==0.0;}, py::arg("x")))
        .def_readwrite("hamiltonian", &Constraint::hamiltonian);
}
