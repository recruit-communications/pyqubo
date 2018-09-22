# Copyright 2018 Recruit Communications Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from operator import or_
import numpy as np
import dimod
from six.moves import reduce


class Model:
    """Model represents binary quadratic optimization problem.
    
    By compiling :class:`Express` object, you get a :class:`Model` object.
    It contains the information about QUBO (or equivalent Ising Model),
    and it also has the function to decode the solution
    into the original variable structure.
    
    Note:
        We do not need to create this object directly. Instead,
        we get this by compiling `Express` objects.
    
    Args:
        compiled_qubo (:class:`.CompiledQubo`):
            Half-compiled QUBO. If we want to get the final QUBO, we need to evaluate this QUBO
            by passing :obj:`params`. See :func:`CompiledQubo.eval()`.
        
        structure (`dict[label, Tuple(key1, key2, key3, ...)]`):
            It defines the mapping of the variable used in :func:`decode_solution`.
            A solution of `label` is mapped to
            :obj:`decoded_solution[key1][key2][key3][...]`.
            For more details, see :func:`decode_solution()`.
        
        constraints (dict[label, polynomial_term]):
            It contains constraints of the problem. `label` is each constraint name and
            `polynomial_term` is corresponding polynomial which should be zero when the
            constraint is satisfied.
    
    Attributes:
        variable_order (list):
            The list of labels. The order is corresponds to the index of QUBO or Ising model.
        
        index2label (dict[int, label]):
            The dictionary which maps an index to a label.
        
        label2index (dict[label, index]):
            The dictionary which maps a label to an index.
    """

    def __init__(self, compiled_qubo, structure, constraints):
        self.compiled_qubo = compiled_qubo
        self.structure = structure
        self.constraints = constraints
        self.variable_order = sorted(self.compiled_qubo.variables)
        self.index2label = dict(enumerate(self.variable_order))
        self.label2index = {v: k for k, v in self.index2label.items()}

    def __repr__(self):
        from pprint import pformat
        return "Model({}, structure={})".format(repr(self.compiled_qubo), str(pformat(self.structure)))

    def _parse_solution(self, solution, var_type):
        """Parse solutions.
        
        Args:
            solution (list[bit]/dict[label, bit]/dict[index, bit]):
                The solution returned from solvers.
            
            var_type (str):
                Specify the variable type. "binary" or "spin".
        
        Returns:
             dict[label, bit]: dictionary of label and binary bit.
        """
        assert var_type in ("binary", "spin"), "var_type should be either 'binary' or 'spin'."

        if isinstance(solution, list) or isinstance(solution, np.ndarray):
            if len(self.variable_order) != len(solution):
                raise ValueError("Illegal solution. Length of the solution is different from"
                                 "that of self.variable_order.")
            dict_solution = dict(zip(self.variable_order, solution))
        elif isinstance(solution, dict):

            if set(solution.keys()) == set(self.variable_order):
                dict_solution = solution

            elif set(solution.keys()) == set(range(len(self.variable_order))):
                dict_solution = {self.index2label[index]: v for index, v in solution.items()}

            else:
                raise ValueError("Illegal solution. The keys of the solution"
                                 " should be same as self.variable_order")
        else:
            raise TypeError("Unexpected type of solution.")

        if var_type == "spin":
            dict_solution = {k: (v + 1) / 2 for k, v in dict_solution.items()}

        return dict_solution

    def energy(self, solution, var_type, params=None):
        """Returns energy of the solution.
        
        Args:
            solution (list[bit]/dict[label, bit]/dict[index, bit]):
                The solution returned from solvers.
            
            var_type (str):
                Specify the variable type. "binary" or "spin".
            
            params (dict[str, float]):
                Specify the parameter values.
        
        Returns:
            float: energy of the solution. 
        """
        dict_solution = self._parse_solution(solution, var_type)
        qubo, offset = self.to_qubo(params=params)
        s = 0.0
        for (label1, label2), value in qubo.items():
            s += dict_solution[label1] * dict_solution[label2] * value
        return s + offset

    def decode_solution(self, solution, var_type, params=None):
        """Returns decoded solution.
        
        Args:
            solution (list[bit]/dict[label, bit]/dict[index, bit]):
                The solution returned from solvers.
            
            var_type (str):
                Specify the input and output variable type. "binary" or "spin".
            
            params (dict[str, float]):
                Specify the parameter values.
                
        Returns:
            tuple(dict, dict, float): Tuple of the decoded solution,
            broken constraints and energy.
            Structure of decoded_solution is defined by :obj:`structure`.
        """

        def put_value_with_keys(dict_body, keys, value):
            for key in keys[:-1]:
                if key not in dict_body:
                    dict_body[key] = {}
                dict_body = dict_body[key]
            dict_body[keys[-1]] = value

        def evaluate_constraint(constraint, dict_value):
            e = 0.0
            for term_key, value in constraint.items():
                e += term_key.calc_product(dict_value) * value
            return e

        decoded_solution = {}

        dict_bin_solution = self._parse_solution(solution, var_type)

        for label, bit in dict_bin_solution.items():
            if label in self.structure:
                if var_type == "spin":
                    out_value = 2 * bit - 1
                elif var_type == "binary":
                    out_value = bit
                else:  # pragma: no cover
                    raise ValueError("var_type should be either 'binary' or 'spin'.")
                put_value_with_keys(decoded_solution, self.structure[label], out_value)

        # Check satisfaction of constraints
        broken_const = {}
        for label, const in self.constraints.items():
            energy = evaluate_constraint(const, dict_bin_solution)
            if energy > 0.0:
                result_value = {var: dict_bin_solution[var] for var in
                                reduce(or_, [k.keys for k in const.keys()])}
                broken_const[label] = {"result": result_value, "penalty": energy}
            elif energy < 0.0:
                raise ValueError("The energy of the constraint \"{label}\" is {energy}."
                                 "But an energy of constraints should not be negative."
                                 .format(label=label, energy=energy))

        problem_energy = self.energy(dict_bin_solution, "binary", params)

        return decoded_solution, broken_const, problem_energy

    def decode_dimod_response(self, response, topk=None):
        """Decode the solution of :class:`dimod.Response`.
        
        For more details about :class:`dimod.Response`,
        see `dimod.Response 
        <https://dimod.readthedocs.io/en/latest/reference/response.html>`_.
        
        Args:
            response (:class:`dimod.Response`):
                The solution returned from dimod sampler.
            topk (int, default=None):
                Decode only top-k (energy is smaller) solutions.
        
        Returns:
            list[tuple(dict, dict, float)]: List of tuple of the decoded solution and
            broken constraints and energy. Solutions are sorted by energy.
            Structure of decoded_solution is defined by :obj:`structure`.
        """
        top_indices = np.argsort(response.record.energy)
        if topk:
            top_indices = top_indices[:topk]

        dict_solutions = list(dict(zip(response.variable_labels, sample)) for sample in response.record.sample[top_indices])

        decoded_solutions = []
        for sol in dict_solutions:
            if response.vartype == dimod.SPIN:
                var_type = "spin"
            else:
                var_type = "binary"
            decoded_solutions.append(self.decode_solution(sol, var_type))
        return decoded_solutions

    def to_dimod_bqm(self, params=None):
        """Returns :class:`dimod.BinaryQuadraticModel`.
        
        For more details about :class:`dimod.BinaryQuadraticModel`,
        see `dimod.BinaryQuadraticModel 
        <https://dimod.readthedocs.io/en/latest/reference/binary_quadratic_model.html>`_.
        
        Args:
            params (dict[str, float]):
                If the expression contains :class:`Param` objects,
                you have to specify the value of them by :obj:`params`.
        
        Returns:
            :class:`dimod.BinaryQuadraticModel` with vartype set to `dimod.BINARY`.
        """
        return self.compiled_qubo.eval(params)

    def to_qubo(self, index_label=False, params=None):
        """Returns QUBO and energy offset.
        
        Args:
            index_label (bool):
                If true, the keys of returned QUBO are indexed with a positive integer number.
            
            params (dict[str, float]):
                If the expression contains :class:`Param` objects,
                you have to specify the value of them by :obj:`params`.
        
        Returns:
            tuple(QUBO, float): Tuple of QUBO and energy offset.
            QUBO takes the form of ``dict[(label, label), value]``.
        
        Examples:
            This example creates the :obj:`model` from the expression, and
            we get the resulting QUBO by calling :func:`model.to_qubo()`.
            
            >>> from pyqubo import Qbit
            >>> x, y, z = Qbit("x"), Qbit("y"), Qbit("z")
            >>> model = (x*y + y*z + 3*z).compile()
            >>> pprint(model.to_qubo())
            ({('x', 'x'): 0.0,
              ('x', 'y'): 1.0,
              ('y', 'y'): 0.0,
              ('y', 'z'): 1.0,
              ('z', 'z'): 3.0},
             0.0)
            
            If you want a QUBO which has index labels, specify the argument ``index_label=True``.
            The mapping of the indices and the corresponding labels is
            stored in :obj:`model.variable_order`.
            
            >>> pprint(model.to_qubo(index_label=True))
            ({(0, 0): 0.0, (0, 1): 1.0, (1, 1): 0.0, (1, 2): 1.0, (2, 2): 3.0}, 0.0)
            >>> model.variable_order
            ['x', 'y', 'z']
            
        """

        bqm = self.compiled_qubo.eval(params)
        q, offset = bqm.to_qubo()

        # Evaluate values of QUBO
        qubo = {}
        for (label1, label2), v in q.items():
            if index_label:
                i = self.label2index[label1]
                j = self.label2index[label2]
            else:
                i = label1
                j = label2
            qubo[(i, j)] = v

        return qubo, offset

    def to_ising(self, index_label=False, params=None):
        """Returns Ising Model and energy offset.

        Args:
            index_label (bool):
                If true, the keys of returned Ising model are
                indexed with a positive integer number.
            
            params (dict[str, float]):
                If the expression contains :class:`Param` objects,
                you have to specify the value of them by :obj:`params`.

        Returns:
            tuple(linear, quadratic, float):
                Tuple of Ising Model and energy offset. Where `linear` takes the form of
                ``(dict[label, value])``, and `quadratic` takes the form of
                ``dict[(label, label), value]``.

        Examples:
            This example creates the :obj:`model` from the expression, and
            we get the resulting Ising model by calling :func:`model.to_ising()`.
            
            >>> from pyqubo import Qbit
            >>> x, y, z = Qbit("x"), Qbit("y"), Qbit("z")
            >>> model = (x*y + y*z + 3*z).compile()
            >>> pprint(model.to_ising())
            ({'x': 0.25, 'y': 0.5, 'z': 1.75}, {('x', 'y'): 0.25, ('y', 'z'): 0.25}, 2.0)
            
            If you want a Ising model which has index labels,
            specify the argument ``index_label=True``.
            The mapping of the indices and the corresponding labels is
            stored in :obj:`model.variable_order`.
            
            >>> pprint(model.to_ising(index_label=True))
            ({0: 0.25, 1: 0.5, 2: 1.75}, {(0, 1): 0.25, (1, 2): 0.25}, 2.0)
            >>> model.variable_order
            ['x', 'y', 'z']

        """

        bqm = self.compiled_qubo.eval(params)
        linear, quadratic, offset = bqm.to_ising()

        # Construct linear
        new_linear = {}
        for label, v in linear.items():
            if index_label:
                i = self.label2index[label]
            else:
                i = label
            new_linear[i] = v

        # Construct quadratic
        new_quadratic = {}
        for (label1, label2), v in quadratic.items():
            if index_label:
                i = self.label2index[label1]
                j = self.label2index[label2]
            else:
                i = label1
                j = label2
            new_quadratic[(i, j)] = v

        return new_linear, new_quadratic, offset


class CompiledQubo:
    """Half-compiled QUBO.
    
    Args:
        qubo (dict[label, :class:`Coefficient`/float]): QUBO
        
        offset (:class:`Coefficient`/float): Offset of QUBO
    
    Attributes:
        qubo (dict[label, :class:`Coefficient`/float]): QUBO
        
        offset (:class:`Coefficient`/float): Offset of QUBO
    
    This contains QUBO and the offset, but the value of the QUBO
    has not been evaluated yet. To get the final QUBO, you need to
    evaluate this QUBO by calling :func:`CompiledQubo.eval`.
    """

    def __init__(self, qubo, offset):
        self.qubo = qubo
        self.offset = offset

    @property
    def variables(self):
        """Unique labels contained in keys of QUBO."""
        return [i for (i, j) in self.qubo.keys() if i == j]

    def eval(self, params):
        """Returns evaluated QUBO.
        
        Args:
            params (dict[str, float]): Pass the value of the parameter.
        
        Returns:
            :class:`BinaryQuadraticModel`
        """
        evaluated_qubo = {}
        for k, v in self.qubo.items():
            evaluated_qubo[k] = CompiledQubo._eval_if_not_float(v, params)

        evaluated_offset = CompiledQubo._eval_if_not_float(self.offset, params)

        return dimod.BinaryQuadraticModel.from_qubo(
            evaluated_qubo, evaluated_offset)

    def __repr__(self):
        from pprint import pformat
        return "CompiledQubo({}, offset={})".format(pformat(self.qubo), self.offset)

    @staticmethod
    def _eval_if_not_float(v, params):
        """ If v is not float (i.e. v is :class:`Express`), returns an evaluated value.

        Args:
            v (float/:class:`Coefficient`):
                The value to be evaluated.
                
            params (dict[str, float]):
                Parameters for evaluation.

        Returns:
            float: Evaluated value of the input :obj:`v`:
        """
        if isinstance(v, float):
            return v
        else:
            return v.eval(params)
