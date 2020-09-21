#include <iostream>
#include <express.h>
#include <poly.h>
#include <time.h>
#include <model.h>
#include <expanded.h>

using namespace::std;

/*---------- Base ------------*/
BasePtr Base::add(BasePtr other){
    //cout << "Base::add\n";
    BasePtr this_ptr = shared_from_this();
    AddPtr new_base(new Add(this_ptr, other));
    return new_base;
}

BasePtr Base::add(double other){
    shared_ptr<Num> num(new Num(other));
    BasePtr this_ptr = shared_from_this();
    if(other == 0.0){
        return this_ptr;
    }else{
        AddPtr new_base(new Add(this_ptr, num));
        return new_base;
    }
}

BasePtr Base::mul(BasePtr other){
    BasePtr this_ptr = shared_from_this();
    shared_ptr<Mul> new_base(new Mul(this_ptr, other));
    return new_base;
}

BasePtr Base::mul(double other){
    BasePtr this_ptr = shared_from_this();
    if(other == 1.0){
        return this_ptr;
    }else if(other == 0.0){
        shared_ptr<Num> num(new Num(0.0));
        return num;
    }else{
        shared_ptr<Num> num(new Num(other));
        shared_ptr<Mul> new_base(new Mul(this_ptr, num));
        return new_base;
    }
}

BasePtr Base::div(double other){
    if(other == 0.0){
        throw std::runtime_error("zero devide error");
    }else{
        return Base::mul(1.0 / other);
    }
}

BasePtr Base::pow(int other){
    BasePtr result = shared_from_this();
    BasePtr this_ptr = shared_from_this(); 
    for(int i=0; i < other-1; i++){
        result = result->mul(this_ptr); 
    }
    return result;
}

BasePtr Base::neg(){
    return Base::mul(-1.0);
}

BasePtr Base::sub(BasePtr other){
    BasePtr this_ptr = shared_from_this();
    AddPtr new_base(new Add(this_ptr, other->mul(-1)));
    return new_base;
}

BasePtr Base::sub(double other){
    return Base::add(-other);
}

BasePtr Base::rsub(double other){
    BasePtr this_ptr = shared_from_this();
    shared_ptr<Num> num(new Num(other));
    AddPtr new_base(new Add(this_ptr->mul(-1), num));
    return new_base;
}

Model Base::compile(double strength){
    CoeffPtr strength_coeff = make_shared<CoeffNum>(strength);
    return Base::compile(strength_coeff);
}

Model Base::compile(string placeholder_label){
    CoeffPtr strength_coeff = make_shared<CoeffPlaceholder>(placeholder_label);
    return Base::compile(strength_coeff);
}

Model Base::compile(CoeffPtr strength){
    clock_t start = clock();
    printf("clock\n");
    Encoder* encoder = new Encoder();
    printf("encoder\n");
    Expanded* expanded = this->expand(encoder);
    clock_t end = clock();
    printf("compile0 %lf[ms]\n", static_cast<double>(end-start) / CLOCKS_PER_SEC * 1000.0);
    CompiledQubo* compiled_qubo = expanded->get_compiled_qubo(encoder, strength);
    clock_t end2 = clock();
    printf("compile1 %lf[ms]\n", static_cast<double>(end2-end) / CLOCKS_PER_SEC * 1000.0);
    return Model(compiled_qubo, encoder, expanded);
}

/*---------- Add ------------*/
BasePtr Add::add(BasePtr other){
    BasePtr this_ptr = shared_from_this();
    AddPtr new_base(new Add(static_pointer_cast<Add>(this_ptr), other));
    return new_base;
}

Expanded* Add::expand(Encoder* encoder){
    //printf("Add::expand\n");
    int i = 0;
    AddList* next_node = this->node;
    //printf("Add::expand1\n");
    //std::cout << next_node->value->to_string(true) << std::endl;
    Expanded* new_expanded = next_node->value->expand(encoder);
    //printf("Add::expand2\n");
    next_node = next_node->next;
    while(next_node != nullptr){
        //printf("Add::loop\n");
        Expanded* expanded_tmp = next_node->value->expand(encoder);
        expanded::add(new_expanded, expanded_tmp);
        next_node = next_node->next;
        i++;
    }
    //printf("Add::expand -3 %s\n", new_expanded->to_string().c_str());
    return new_expanded;
};

/*---------Mul------------*/
Expanded* Mul::expand(Encoder* encoder){
    //printf("Mul::expand\n");
    Expanded* left_expanded = this->left->expand(encoder);
    //printf("Mul::expand -left %s\n", left_expanded->to_string().c_str());

    Expanded* right_expanded = this->right->expand(encoder);
    //printf("Mul::expand -right %s\n", right_expanded->to_string().c_str());

    Expanded* new_expanded = expanded::mul(left_expanded, right_expanded);
    return new_expanded;
};

/*---------Binary------------*/
Expanded* Binary::expand(Encoder* encoder){
    BasePtr this_ptr = shared_from_this();
    //printf("Binary::expand1\n");
    Mono* poly = new Mono(static_pointer_cast<Binary>(this_ptr), encoder);
    //printf("Binary::expand2 %s\n", poly->to_string().c_str());
    auto new_expanded = new Expanded(poly);
    return new_expanded;
};

Expanded* Spin::expand(Encoder* encoder){
    BasePtr this_ptr = shared_from_this();
    Poly* poly = new Poly(static_pointer_cast<Spin>(this_ptr), encoder);
    auto new_expanded = new Expanded(poly);
    return new_expanded;
};

/*---------Num------------*/
Expanded* Num::expand(Encoder* encoder){
    BasePtr this_ptr = shared_from_this();
    //unique_ptr<SinglePoly> poly = unique_ptr<SinglePoly>(new SinglePoly(static_pointer_cast<Num>(this_ptr)));
    Mono* poly = new Mono(static_pointer_cast<Num>(this_ptr));
    return new Expanded(poly);
};

/*---------Placeholder------------*/
Expanded* Placeholder::expand(Encoder* encoder){
    BasePtr this_ptr = shared_from_this();
    Mono* poly = new Mono(static_pointer_cast<Placeholder>(this_ptr));
    return new Expanded(poly);
};

Expanded* WithPenalty::expand(Encoder* encoder){
    this->check_instance_variable();
    Expanded* hamiltonian_expand = this->hamiltonian->expand(encoder);
    Expanded* penalty_expanded = penalty->expand(encoder);
    
    hamiltonian_expand->add_penalty(penalty_expanded);
    return hamiltonian_expand;
};


Expanded* UserDefinedExpress::expand(Encoder* encoder){
    this->check_instance_variable();
    Expanded* hamiltonian_expand = this->hamiltonian->expand(encoder);
    return hamiltonian_expand;
};

Expanded* SubH::expand(Encoder* encoder){
    SubH::check_instance_variable();
    Expanded* hamiltonian_exp = this->hamiltonian->expand(encoder);
    hamiltonian_exp->add_sub_h(this->label, hamiltonian_exp->poly->get_terms(), nullptr);
    //cout << "SubH::expand " << std::to_string(hamiltonian_poly->compiled_sub_hs.size()) << "\n";
    return hamiltonian_exp;
};

Expanded* Constraint::expand(Encoder* encoder){
    //Constraint::check_instance_variable();
    Expanded* hamiltonian_exp = this->hamiltonian->expand(encoder);
    hamiltonian_exp->add_sub_h(this->label, hamiltonian_exp->poly->get_terms(), this->condition);
    //cout << "SubH::expand " << std::to_string(hamiltonian_poly->compiled_sub_hs.size()) << "\n";
    return hamiltonian_exp;
};