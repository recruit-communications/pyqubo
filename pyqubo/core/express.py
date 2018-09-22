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

import abc
import copy
from collections import defaultdict
from operator import or_, xor
from six.moves import reduce
import dimod
import six

from .coefficient import Coefficient
from .model import Model, CompiledQubo
from .binaryprod import BinaryProd
from .paramprod import ParamProd


@six.add_metaclass(abc.ABCMeta)
class Express:
    """Abstract class of pyqubo expression.
    
    All basic component class such as :class:`.Qbit`, :class:`.Spin` or :class:`.Add`
    inherits :class:`.Express`.
    
    .. graphviz::
    
        digraph {
            graph [size="2.5, 2.5"]
            node [shape=rl]
            add [label=AddList]
            qbit_a [label="Qbit(a)"]
            qbit_b [label="Qbit(b)"]
            mul_1 [label="Mul"]
            mul_2 [label="Mul"]
            num_1 [label="Num(1)"]
            num_2 [label="Num(2)"]
            add -> num_1
            add -> mul_1
            mul_1 -> mul_2
            mul_1 -> qbit_a
            mul_2 -> qbit_b
            mul_2 -> num_2
        }
    
    For example, an expression :math:`2ab+1` (where :math:`a, b` is :class:`Qbit` variable) is
    represented by the binary tree above.
    
    Note:
        This class is an abstract class of all component of expressions.
    
    Example:
        We write mathematical expressions with objects such as :class:`Qbit` or :class:`Spin`
        which inherit :class:`.Express`.
        
        >>> from pyqubo import Qbit
        >>> a, b = Qbit("a"), Qbit("b")
        >>> 2*a*b + 1
        (((Qbit(a)*Num(2))*Qbit(b))+Num(1))

    """

    CONST_TERM_KEY = BinaryProd(set())
    PROD_SYM = '*'

    def __init__(self):
        pass

    def __rmul__(self, other):
        """It is called when `other(number) - self`"""
        return self.__mul__(other)

    def __mul__(self, other):
        """It is called when `self * other(any object)`"""
        return Mul(self, other)

    def __rsub__(self, other):
        """It is called when `other(number) - self`"""
        return AddList([Mul(self, -1), other])

    def __sub__(self, other):
        """It is called when `self - other(any object)`"""
        if other == 0.0:
            return self
        else:
            if isinstance(other, Express):
                return self.__add__(Mul(other, -1))
            else:
                return self.__add__(-other)

    def __radd__(self, other):
        """It is called when `other(number) + self`"""
        return self.__add__(other)
    
    def __add__(self, other):
        """It is called when `self + other(any object)`"""
        if other == 0.0:
            return self
        else:
            return AddList([self, other])

    def __pow__(self, order):
        if int(order) == order and order >= 1:
            return reduce(lambda a, b: Mul(a, b), order * [self])
        else:
            raise ValueError("Power of {} th order cannot be done.".format(order))

    def __div__(self, other):
        """It is called when `self / other(any object)`"""
        if not isinstance(other, Express):
            return Mul(self, other ** -1)
        else:
            raise ValueError("Expression cannot be divided by Expression.")

    def __rdiv__(self, other):
        """It is called when `other(number) / self`"""
        raise ValueError("Expression cannot be divided by Expression.")

    def __truediv__(self, other):  # pragma: no cover
        """division in Python3"""
        return self.__div__(other)

    def __rtruediv__(self, other):  # pragma: no cover
        """It is called when `other(number) / self`"""
        return self.__rdiv__(other)

    def __neg__(self):
        """Negative value of expression."""
        return Mul(self, Num(-1))

    def __ne__(self, other):
        return not self.__eq__(other)

    @abc.abstractmethod
    def __repr__(self):  # pragma: no cover
        pass

    @abc.abstractmethod
    def __eq__(self, other):  # pragma: no cover
        pass

    @abc.abstractmethod
    def __hash__(self):  # pragma: no cover
        pass

    def compile(self, strength=5.0):
        """Returns the compiled :class:`Model`.
        
        This method reduces the degree of the expression if the degree is higher than 2,
        and convert it into :class:`.Model` which has information about QUBO.
        
        Args:
            strength (float): The strength of the reduction constraint.
                Insufficient strength can result in the binary quadratic model
                not having the same minimizations as the polynomial.

        Returns:
            :class:`Model`: The model compiled from the :class:`.Express`.
        
        Examples:
            In this example, there is a higher order term :math:`abcd`. It is decomposed as
            [[``a*d``, ``c``], ``b``] hierarchically and converted into QUBO.
            By calling :func:`to_qubo()` of the :obj:`model`, we get the resulting QUBO.
            
            >>> from pyqubo import Qbit
            >>> a, b, c, d = Qbit("a"), Qbit("b"), Qbit("c"), Qbit("d")
            >>> model = (a*b*c + a*b*d).compile()
            >>> pprint(model.to_qubo())
            ({('a', 'a'): 0.0,
              ('a', 'a*b'): -10.0,
              ('a', 'b'): 5.0,
              ('a*b', 'a*b'): 15.0,
              ('a*b', 'b'): -10.0,
              ('a*b', 'c'): 1.0,
              ('a*b', 'd'): 1.0,
              ('b', 'b'): 0.0,
              ('c', 'c'): 0.0,
              ('d', 'd'): 0.0},
             0.0)
        """
        def compile_param_if_express(val):
            if isinstance(val, Express):
                return val._compile_param()
            else:
                return val

        # Constraint for AND(multiplier, multiplicand) = product
        def binary_product(multiplier, multiplicand, product, weight):
            return {
                BinaryProd({product}): 3.0 * weight,
                BinaryProd({multiplicand, product}): -2.0 * weight,
                BinaryProd({multiplier, product}): -2.0 * weight,
                BinaryProd({multiplier, multiplicand}): weight
            }

        # When the label contains PROD_SYM, elements of products should be sorted
        # such that the resulting label is uniquely determined.
        def normalize_label(label):
            s = Express.PROD_SYM
            if s in label:
                return s.join(sorted(label.split(s)))
            else:
                return label

        # Expand the expression to polynomial
        expanded, const = Express._expand(self)

        # Make polynomials quadratic
        offset = 0.0
        pubo = {}
        for term_key, value in expanded.items():
            if term_key.is_constant():
                offset = value
            else:
                pubo[tuple(term_key.keys)] = value
        bqm = dimod.make_quadratic(pubo, strength, dimod.BINARY)
        bqm_qubo, bqm_offset = bqm.to_qubo()

        # Extracts product constrains
        product_consts = {}
        for (a, b), v in bqm.info['reduction'].items():
            prod = normalize_label(v['product'])
            product_consts["AND({},{})={}".format(a, b, prod)]\
                = binary_product(a, b, prod, strength)

        # Normalize labels and compile values of the QUBO
        compiled_qubo = {}
        for (label1, label2), value in bqm_qubo.items():
            norm_label1 = normalize_label(label1)
            norm_label2 = normalize_label(label2)

            # Sort the tuple of labels such that the created key is uniquely determined.
            if norm_label2 > norm_label1:
                label_key = (norm_label1, norm_label2)
            else:
                label_key = (norm_label2, norm_label1)
            # Compile values of the QUBO
            compiled_qubo[label_key] = compile_param_if_express(value)
        compiled_qubo = CompiledQubo(compiled_qubo, compile_param_if_express(offset + bqm_offset))

        # Merge structures
        uniq_variables = Express._unique_vars(self)
        structure = reduce(Express._merge_dict, [var.structure for var in uniq_variables])

        return Model(compiled_qubo, structure, Express._merge_dict(const, product_consts))

    def _compile_param(self):
        expanded, _ = Express._expand_param(self)
        return Coefficient(expanded)

    @staticmethod
    def _merge_dict(dict1, dict2):
        dict1_copy = copy.copy(dict1)
        dict1_copy.update(dict2)
        return dict1_copy

    @staticmethod
    def _merge_dict_update(const1, const2):
        const1.update(const2)
        return const1

    @staticmethod
    def _unique_vars(exp):
        if isinstance(exp, AddList):
            return reduce(or_, [Express._unique_vars(term) for term in exp.terms])
        elif isinstance(exp, Mul):
            return Express._unique_vars(exp.left) | Express._unique_vars(exp.right)
        elif isinstance(exp, Add):
            return Express._unique_vars(exp.left) | Express._unique_vars(exp.right)
        elif isinstance(exp, Param):
            return set()
        elif isinstance(exp, Num):
            return set()
        elif isinstance(exp, Constraint):
            return Express._unique_vars(exp.child)
        elif isinstance(exp, Qbit):
            return {exp}
        elif isinstance(exp, Spin):
            return {exp}
        elif isinstance(exp, UserDefinedExpress):
            return Express._unique_vars(exp.express)
        else:
            raise TypeError("Unexpected input type {}.".format(type(exp)))  # pragma: no cover

    @staticmethod
    def _merge_term(term1, term2):
        if len(term1) < len(term2):
            for k, v in term1.items():
                term2[k] += v
            r = term2
        else:
            for k, v in term2.items():
                term1[k] += v
            r = term1
        return r

    @staticmethod
    def _expand_param(exp):
        """Expand the parameter expression hierarchically into dict format."""

        if isinstance(exp, AddList):
            expanded, const = reduce(
                lambda arg1, arg2:
                (Express._merge_term(arg1[0], arg2[0]), Express._merge_dict_update(arg1[1], arg2[1])),
                [Express._expand_param(term) for term in exp.terms])
            return expanded, const

        elif isinstance(exp, Mul):
            left, left_const = Express._expand_param(exp.left)
            right, right_const = Express._expand_param(exp.right)
            expanded_terms = defaultdict(float)
            for k1, v1 in left.items():
                for k2, v2 in right.items():
                    merged_key = ParamProd.merge_term_key(k1, k2)
                    expanded_terms[merged_key] += v1 * v2
            return expanded_terms, Express._merge_dict_update(left_const, right_const)

        elif isinstance(exp, Param):
            expanded_terms = defaultdict(float)
            expanded_terms[ParamProd({exp.label: 1.0})] = 1.0
            return expanded_terms, {}

        elif isinstance(exp, Num):
            terms = defaultdict(float)
            terms[ParamProd({})] = exp.value
            return terms, {}

        else:
            raise TypeError("Unexpected input type {}.".format(type(exp)))  # pragma: no cover

    @staticmethod
    def _expand(exp):
        """Expand the expression hierarchically into dict format.
        
        For example, ``2*Qbit(a)*Qbit(b) + 1`` is represented as
        dict format ``{BinaryProd(ab): 2.0, CONST_TERM_KEY: 1.0}``.
        
        Let's see how this dict is created step by step.
        First, focus on `2*Qbit(a)*Qbit(b)` in which each expression is expanded as
        _expand(Num(2)) # => {CONST_TERM_KEY: 2.0}
        _expand(Qbit("a")) # => {BinaryProd(a): 1.0}
        _expand(Qbit("b")) # => {BinaryProd(b): 1.0}
        respectively.
        
        :class:`Mul` combines the expression in the following way
        _expand(Mul(Num(2), Qbit("a"))) # => {BinaryProd(a): 2.0}
        _expand(Mul(Qbit("b"), Mul(Num(2), Qbit("a")))) # => {BinaryProd(ab): 2.0}
        
        Finally, :class:`Add` combines the ``{BinaryProd(ab): 2.0}`` and `{CONST_TERM_KEY: 1.0}`,
        and we get the final form {BinaryProd(ab): 2.0, CONST_TERM_KEY: 1.0}
        
        Args:
            exp (:class:`Express`): Input expression.
        
        Returns:
            tuple(expanded_terms, constraints):
                tuple of expanded_terms and constrains. Expanded expression takes the form
                ``dict[:class:`BinaryProd`, value]``.
                Constraints takes the form of ``dict[label, expanded_terms]``.
        
        """

        if isinstance(exp, Add):
            left, left_const = Express._expand(exp.left)
            right, right_const = Express._expand(exp.right)
            result = Express._merge_term(right, left)
            return result, Express._merge_dict_update(left_const, right_const)

        elif isinstance(exp, AddList):
            expanded, const = reduce(
                lambda arg1, arg2:
                (Express._merge_term(arg1[0], arg2[0]), Express._merge_dict_update(arg1[1], arg2[1])),
                [Express._expand(term) for term in exp.terms])
            return expanded, const

        elif isinstance(exp, Mul):
            left, left_const = Express._expand(exp.left)
            right, right_const = Express._expand(exp.right)
            expanded_terms = defaultdict(float)
            for k1, v1 in left.items():
                for k2, v2 in right.items():
                    merged_key = BinaryProd.merge_term_key(k1, k2)
                    expanded_terms[merged_key] += v1 * v2
            return expanded_terms, Express._merge_dict_update(left_const, right_const)

        elif isinstance(exp, Param):
            expanded_terms = defaultdict(float)
            expanded_terms[Express.CONST_TERM_KEY] = exp
            return expanded_terms, {}

        elif isinstance(exp, Constraint):
            child, child_const = Express._expand(exp.child)
            child_const[exp.label] = copy.copy(child)
            return child, child_const

        elif isinstance(exp, Num):
            terms = defaultdict(float)
            terms[Express.CONST_TERM_KEY] = exp.value
            return terms, {}

        elif isinstance(exp, Qbit):
            terms = defaultdict(float)
            terms[BinaryProd({exp.label})] = 1.0
            return terms, {}

        elif isinstance(exp, Spin):
            terms = defaultdict(float)
            terms[BinaryProd({exp.label})] = 2.0
            terms[Express.CONST_TERM_KEY] = -1.0
            return terms, {}

        elif isinstance(exp, UserDefinedExpress):
            return Express._expand(exp.express)

        else:
            raise TypeError("Unexpected input type {}.".format(type(exp)))  # pragma: no cover


class UserDefinedExpress(Express):
    """User Defined Express.
    
    User can define her/his own expression by inheriting :class:`UserDefinedExpress`.
    
    Attributes:
        express (Express): User can define an original expression by defining this member.
        
    Example:
        Define the :class:`LogicalAnd` class by inheriting :class:`UserDefinedExpress`.
        
        >>> from pyqubo import UserDefinedExpress
        >>> class LogicalAnd(UserDefinedExpress):
        ...     def __init__(self, bit_a, bit_b):
        ...         express = bit_a * bit_b
        ...         super(LogicalAnd, self).__init__(express)
    """

    def __init__(self, express):
        assert isinstance(express, Express)
        super(UserDefinedExpress, self).__init__()
        self.express = express

    def __hash__(self):
        return hash(self.express)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        else:
            return self.express == other.express

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.express)


class Param(Express):
    """Parameter expression.
    
    You can specify the value of the :class:`Param` when creating the QUBO.
    By using :class:`Param`, you can change the value without compiling again.
    This is useful when you need to update the strength of constraint gradually.
    
    Args:
        label (str): The label of the parameter.
    
    Example:
        The value of the parameter is specified when you call :func:`to_qubo`.
        
        >>> from pyqubo import Qbit, Param
        >>> x, y, a = Qbit('x'), Qbit('y'), Param('a')
        >>> exp = a*x*y + 2*x
        >>> pprint(exp.compile().to_qubo(params={'a': 3}))
        ({('x', 'x'): 2.0, ('x', 'y'): 3.0, ('y', 'y'): 0.0}, 0.0)
        >>> pprint(exp.compile().to_qubo(params={'a': 5}))
        ({('x', 'x'): 2.0, ('x', 'y'): 5.0, ('y', 'y'): 0.0}, 0.0)
    """

    def __init__(self, label):
        super(Param, self).__init__()
        self.label = label

    def __hash__(self):
        return hash(self.label)

    def __eq__(self, other):
        if not isinstance(other, Param):
            return False
        else:
            return self.label == other.label

    def __repr__(self):
        return "Param({})".format(self.label)


class Constraint(Express):
    """Constraint expression.
    
    You can specify the constraint part in your expression.
    
    Args:
        child (:class:`Express`): The expression you want to specify as a constraint.
        
        label (str): The label of the constraint. You can identify constraints by the label.
    
    Example:
        When the solution is broken, `decode_solution` can detect it.
        In this example, we introduce a constraint :math:`a+b=1`.
        
        >>> from pyqubo import Qbit, Constraint
        >>> a, b = Qbit('a'), Qbit('b')
        >>> exp = a + b + Constraint((a+b-1)**2, label="one_hot")
        >>> model = exp.compile()
        >>> sol, broken, energy = model.decode_solution({'a': 1, 'b': 1}, var_type='binary')
        >>> pprint(broken)
        {'one_hot': {'penalty': 1.0, 'result': {'a': 1, 'b': 1}}}
        >>> sol, broken, energy = model.decode_solution({'a': 1, 'b': 0}, var_type='binary')
        >>> pprint(broken)
        {}
    """

    def __init__(self, child, label):
        assert isinstance(label, str), "label should be string."
        assert isinstance(child, Express), "child should be an Express instance."
        super(Constraint, self).__init__()
        self.child = child
        self.label = label

    def __hash__(self):
        return hash(self.label) ^ hash(self.child)

    def __eq__(self, other):
        if not isinstance(other, Constraint):
            return False
        else:
            return self.label == other.label and self.child == other.child

    def __repr__(self):
        return "Const({}, {})".format(self.label, repr(self.child))


class Spin(Express):
    """Spin variable i.e. {-1, 1}.
    
    Args:
        label (str): The label of a variable. A variable is identified by this label.
        
        structure (dict/optional): Variable structure.
    
    Example:
        >>> from pyqubo import Spin
        >>> a, b = Spin('a'), Spin('b')
        >>> exp = 2*a*b + 3*a
        >>> pprint(exp.compile().to_qubo())
        ({('a', 'a'): 2.0, ('a', 'b'): 8.0, ('b', 'b'): -4.0}, -1.0)
    """

    def __init__(self, label, structure=None):
        assert isinstance(label, str), "label should be string."
        assert Express.PROD_SYM not in label, "label should not contain {}".format(Express.PROD_SYM)
        super(Spin, self).__init__()
        if not structure:
            # if no structure is given
            self.structure = {label: (label,)}
        else:
            self.structure = structure
        self.label = label

    def __repr__(self):
        return "Spin({})".format(self.label)

    def __hash__(self):
        return hash(self.label)

    def __eq__(self, other):
        """Returns whether the label is same or not."""
        if not isinstance(other, Spin):
            return False
        else:
            return self.label == other.label


class Qbit(Express):
    """Binary variable i.e. {0, 1}.
    
    Args:
        label (str): The label of a variable. A variable is identified by this label.
        
        structure (dict/optional): Variable structure.
    
    Example:
        >>> from pyqubo import Qbit
        >>> a, b = Qbit('a'), Qbit('b')
        >>> exp = 2*a*b + 3*a
        >>> pprint(exp.compile().to_qubo())
        ({('a', 'a'): 3.0, ('a', 'b'): 2.0, ('b', 'b'): 0.0}, 0.0)
    """

    def __init__(self, label, structure=None):
        assert isinstance(label, str), "Label should be string."
        assert Express.PROD_SYM not in label, "label should not contain {}".format(Express.PROD_SYM)
        super(Qbit, self).__init__()
        if not structure:
            # if no structure is given
            self.structure = {label: (label,)}
        else:
            self.structure = structure
        self.label = label

    def __repr__(self):
        return "Qbit({})".format(self.label)

    def __hash__(self):
        return hash(self.label)

    def __eq__(self, other):
        """Returns whether the label is same or not."""
        if not isinstance(other, Qbit):
            return False
        else:
            return self.label == other.label


class Mul(Express):
    """Product of expressions.
    
    Args:
        left (:class:`Express`): An expression
        
        right (:class:`Express`): An expression

    Example:        
        You can multiply expressions with either the built-in operator or :class:`Mul`.
        
        >>> from pyqubo import Qbit, Mul
        >>> a, b = Qbit('a'), Qbit('b')
        >>> a * b
        (Qbit(a)*Qbit(b))
        >>> Mul(a, b)
        (Qbit(a)*Qbit(b))
    """

    def __init__(self, left, right):
        super(Mul, self).__init__()
        # When right is a number (non-Express). (Only right can be a number.)
        if isinstance(left, Express) and not isinstance(right, Express):
            self.left = left
            self.right = Num(right)

        # When both arguments are Express.
        elif isinstance(left, Express) and isinstance(right, Express):
            self.left = left
            self.right = right
        else:
            raise ValueError("left should be an Express instance.")

    def __repr__(self):
        return "({}*{})".format(repr(self.left), repr(self.right))

    def __hash__(self):
        return hash(self.left) ^ hash(self.right)

    def __eq__(self, other):
        if not isinstance(other, Mul):
            return False
        elif self.left == other.left and self.right == other.right:
            return True
        elif self.right == other.left and self.left == other.right:
            return True
        else:
            return False


class Add(Express):
    """Addition of expressions (deprecated).
    
    Args:
        left (:class:`Express`): An expression
        
        right (:class:`Express`): An expression
    
    Example:
        You can add expressions with either the built-in operator or :class:`Add`.
        
        >>> from pyqubo import Qbit, Add
        >>> a, b = Qbit('a'), Qbit('b')
        >>> a + b
        (Qbit(a)+Qbit(b))
        >>> Add(a, b)
        (Qbit(a)+Qbit(b))
    
    """

    def __init__(self, left, right):
        super(Add, self).__init__()
        # When right is a number (non-Express). (Only right can be a number.)
        if isinstance(left, Express) and not isinstance(right, Express):
            self.left = left
            self.right = Num(right)

        # When both arguments are Express.
        elif isinstance(left, Express) and isinstance(right, Express):
            self.left = left
            self.right = right
        else:
            raise ValueError("left should be an Express instance.")

    def __hash__(self):
        return hash(self.left) ^ hash(self.right)

    def __repr__(self):
        return "({}+{})".format(repr(self.left), repr(self.right))

    def __eq__(self, other):
        if not isinstance(other, Add):
            return False
        elif self.left == other.left and self.right == other.right:
            return True
        elif self.right == other.left and self.left == other.right:
            return True
        else:
            return False


class AddList(Express):
    """Addition of a list of expressions.
    
    Args:
        terms (list[:class:`Express`]): a list of expressions
    
    Example:
        You can add expressions with either the built-in operator or :class:`AddList`.
        
        >>> from pyqubo import Qbit, AddList
        >>> a, b = Qbit('a'), Qbit('b')
        >>> a + b
        (Qbit(a)+Qbit(b))
        >>> AddList([a, b])
        (Qbit(a)+Qbit(b))
    """

    def __init__(self, terms):
        super(AddList, self).__init__()
        new_terms = []
        for term in terms:
            if isinstance(term, Express):
                new_terms.append(term)
            else:
                new_terms.append(Num(term))
        self.terms = new_terms

    def __add__(self, other):
        """ Override __add__().
        
        To prevent a deep nested expression, __add__() returns AddList object
        where the added expression object is appended to :obj:`terms`.
        
        Returns:
            :class:`AddList`
        """
        if other == 0.0:
            return self
        else:
            if not isinstance(other, Express):
                other = Num(other)
            return AddList(self.terms + [other])

    def __hash__(self):
        return reduce(xor, [hash(term) for term in self.terms])

    def __repr__(self):
        return "({})".format("+".join([repr(e) for e in self.terms]))

    def __eq__(self, other):
        if not isinstance(other, AddList):
            return False
        else:
            return set(self.terms) == set(other.terms)


class Num(Express):
    """Expression of number
    
    Args:
        value (float): the value of the number.
    
    Example:
        >>> from pyqubo import Qbit, Num
        >>> a = Qbit('a')
        >>> a + 1
        (Qbit(a)+Num(1))
        >>> a + Num(1)
        (Qbit(a)+Num(1))
    """
    def __init__(self, value):
        super(Num, self).__init__()
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return "Num({})".format(str(self.value))

    def __eq__(self, other):
        if not isinstance(other, Num):
            return False
        else:
            return self.value == other.value

