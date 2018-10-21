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

from .core import Spin, Qbit, Express

import dimod
from dimod.decorators import vartype_argument
import numpy as np


class Array:
    """Multi-dimensional array.

    Args:
        bit_list (list/:class:`numpy.ndarray`): The object from which a new array is created.
            Accepted input:
        
                * (Nested) list of :class:`Express` or int or float.
                * numpy.ndarray

    Attributes:
        shape (tuple[int]): Shape of this array.

    Example:
        
        Create an Array from a nested list of :class:`Express`.
        
        >>> from pyqubo import Array, Qbit
        >>> array = Array([[Qbit('x0'), Qbit('x1')], [Qbit('x2'), Qbit('x3')]])
        >>> array
        Array([[Qbit(x0), Qbit(x1)],
               [Qbit(x2), Qbit(x3)]])
        
        Get the shape of the array.
        
        >>> array.shape
        (2, 2)
        
        Access an element with index.
        
        >>> array[0, 0]
        Qbit(x0)
        
        Use slice ":" to select a subset of the array.
        
        >>> array[:, 1]
        Array([Qbit(x1), Qbit(x3)])
        >>> sum(array[:, 1])
        (Qbit(x1)+Qbit(x3))
        
        Use list or tuple to select a subset of the array.

        >>> array[[0, 1], 1]
        Array([Qbit(x1), Qbit(x3)])
        >>> array[(0, 1), 1]
        Array([Qbit(x1), Qbit(x3)])
        
        Create an array from numpy array.
        
        >>> import numpy as np
        >>> Array(np.array([[1, 2], [3, 4]]))
        Array([[1, 2],
               [3, 4]])
    """

    def __init__(self, bit_list):

        if isinstance(bit_list, np.ndarray):
            self.shape = bit_list.shape
            self.bit_list = bit_list.tolist()

        elif isinstance(bit_list, list):
            def get_shape(l):
                if isinstance(l, list):
                    length = len(l)
                    shape_set = {get_shape(e) for e in l}
                    if len(shape_set) == 1:
                        sub_shape = shape_set.pop()
                        return tuple([length] + list(sub_shape))
                    else:
                        raise ValueError('Cannot determine the shape of input nested list.')
                else:
                    return tuple()
            self.shape = get_shape(bit_list)
            self.bit_list = bit_list

        else:
            raise TypeError('argument should be ndarray or list')

    def __len__(self):
        return self.shape[0]

    def __getitem__(self, key):
        """Get a subset of this array.
        
        Args:
            key (int/tuple[int]): Index of array.
        
        Returns:
            :class:`Express`/:class:`Array`/int/float
        
        Example:
            >>> array = Array.create('x', (2, 3, 2), 'BINARY')
            >>> array
            Array([[[Qbit(x[0][0][0]), Qbit(x[0][0][1])],
                    [Qbit(x[0][1][0]), Qbit(x[0][1][1])],
                    [Qbit(x[0][2][0]), Qbit(x[0][2][1])]],
            
                   [[Qbit(x[1][0][0]), Qbit(x[1][0][1])],
                    [Qbit(x[1][1][0]), Qbit(x[1][1][1])],
                    [Qbit(x[1][2][0]), Qbit(x[1][2][1])]]])
            >>> array[0, 1, 1]
            Qbit(x[0][1][1])
            >>> array[:, :, 1]
            
        """
        if isinstance(key, int):
            key = key,
        elif not isinstance(key, tuple):
            raise TypeError("Key should be int or tuple of int")

        def get_item(l, index):
            if len(index) > 1:
                current_index = index[0]
                if isinstance(current_index, int):
                    return get_item(l[current_index], index[1:])
                elif isinstance(current_index, list) or isinstance(current_index, tuple):
                    return [get_item(l[i], index[1:]) for i in current_index]
                else:
                    return [get_item(e, index[1:]) for e in l[current_index]]
            else:
                return l[index[0]]

        item = get_item(self.bit_list, key)

        if isinstance(item, list):
            return Array(item)
        else:
            return item

    def __repr__(self):
        nest_depth = len(self.shape)
        offset = len("Array(")

        def format_nested_list(nested_list, nest_count):
            if isinstance(nested_list[0], list):
                return '[{body}]'.format(
                    body=',{line_feed}{indent}'.format(
                        indent=' ' * (nest_count + offset),
                        line_feed='\n' * (nest_depth - nest_count)
                    ).join([format_nested_list(sub_list, nest_count+1) for sub_list in nested_list])
                )
            else:
                return '[%s]' % ', '.join(map(str, nested_list))

        return 'Array({body})'.format(body=format_nested_list(self.bit_list, 1))

    def __eq__(self, other):
        if not isinstance(other, Array):
            return False
        else:
            return self.bit_list == other.bit_list

    def __ne__(self, other):
        return not self.__eq__(other)

    # math operation
    def __neg__(self):
        minus_one = Array.fill(-1, self.shape)
        #return self._pairwise_op_with_type_check(minus_one, lambda x, y: x * y)
        return self * minus_one

    def __radd__(self, other):
        """It is called when `other(number) + self`"""
        return self.__add__(other)

    def __add__(self, other):
        """It is called when `self + other(any object)`"""
        return self.add(other)

    def __rsub__(self, other):
        """It is called when `other(number) - self`"""
        return (-self).add(other)

    def __sub__(self, other):
        """It is called when `self - other(any object)`"""
        return self.subtract(other)

    def __rmul__(self, other):
        """It is called when `other(number) * self`"""
        return self.__mul__(other)

    def __mul__(self, other):
        """It is called when `self * other(any object)`"""
        return self.mul(other)

    def __div__(self, other):
        """It is called when `self / other(any object)`"""
        if not isinstance(other, Array):
            return self * (other ** -1)
        else:
            raise ValueError("Expression cannot be divided by Expression.")

    def __rdiv__(self, other):
        """It is called when `other(number) / self`"""
        raise ValueError("Number cannot be divided by Expression.")

    def __truediv__(self, other):  # pragma: no cover
        """division in Python3"""
        return self.__div__(other)

    def __rtruediv__(self, other):  # pragma: no cover
        """It is called when `other(number) / self`"""
        return self.__rdiv__(other)

    def add(self, other):
        """Returns a sum of self and other.
        
        Args:
            other (:class:`Array`/:class:`ndarray`/int/float): Addend.
        
        Returns:
            :class:`Array`
        
        Example:
            
            >>> from pyqubo import Array
            >>> array_a = Array([[Qbit('a'), Qbit('b')], [Qbit('c'), 2]])
            >>> array_b = Array([[Qbit('d'), 1], [Qbit('f'), Qbit('g')]])
            >>> array_a.add(array_b)
            Array([[(Qbit(a)+Qbit(d)), (Qbit(b)+Num(1))],
                   [(Qbit(c)+Qbit(f)), (Qbit(g)+Num(2))]])
            >>> array_a + array_b
            Array([[(Qbit(a)+Qbit(d)), (Qbit(b)+Num(1))],
                   [(Qbit(c)+Qbit(f)), (Qbit(g)+Num(2))]])

            Sum of self and scalar value.
            
            >>> array_a + 5
            Array([[(Qbit(a)+Num(5)), (Qbit(b)+Num(5))],
                   [(Qbit(c)+Num(5)), 7]])
            
            Sum of self and numpy ndarray.
            
            >>> array_a + np.array([[1, 2], [3, 4]])
            Array([[(Qbit(a)+Num(1)), (Qbit(b)+Num(2))],
                   [(Qbit(c)+Num(3)), 6]])
        """
        return self._pairwise_op_with_type_check(other, lambda x, y: x + y)

    def subtract(self, other):
        """Returns a difference between other and self.

        Args:
            other (:class:`Array`/:class:`ndarray`/int/float): Subtrahend.

        Returns:
            :class:`Array`

        Example:

            >>> from pyqubo import Array
            >>> array_a = Array([[Qbit('a'), Qbit('b')], [Qbit('c'), 2]])
            >>> array_b = Array([[Qbit('d'), 1], [Qbit('f'), Qbit('g')]])
            >>> array_a.subtract(array_b)
            Array([[(Qbit(a)+(Qbit(d)*Num(-1))), (Qbit(b)+Num(-1))],
                   [(Qbit(c)+(Qbit(f)*Num(-1))), ((Qbit(g)*Num(-1))+Num(2))]])
            >>> array_a - array_b
            Array([[(Qbit(a)+(Qbit(d)*Num(-1))), (Qbit(b)+Num(-1))],
                   [(Qbit(c)+(Qbit(f)*Num(-1))), ((Qbit(g)*Num(-1))+Num(2))]])

            Difference of self and scalar value.
            
            >>> array_a - 5
            Array([[(Qbit(a)+Num(-5)), (Qbit(b)+Num(-5))],
                   [(Qbit(c)+Num(-5)), -3]])
            
            Difference of self and numpy ndarray.
            
            >>> array_a - np.array([[1, 2], [3, 4]])
            Array([[(Qbit(a)+Num(-1)), (Qbit(b)+Num(-2))],
                   [(Qbit(c)+Num(-3)), -2]])
        """
        return self._pairwise_op_with_type_check(other, lambda x, y: x - y)

    def mul(self, other):
        """Returns a multiplicity of self by other.

        Args:
            other (:class:`Array`/:class:`ndarray`/int/float): Factor.

        Returns:
            :class:`Array`

        Example:

            >>> from pyqubo import Array
            >>> array_a = Array([[Qbit('a'), Qbit('b')], [Qbit('c'), 2]])
            >>> array_b = Array([[Qbit('d'), 1], [Qbit('f'), Qbit('g')]])
            >>> array_a.mul(array_b)
            Array([[(Qbit(a)*Qbit(d)), (Qbit(b)*Num(1))],
                   [(Qbit(c)*Qbit(f)), (Qbit(g)*Num(2))]])
            >>> array_a * array_b
            Array([[(Qbit(a)*Qbit(d)), (Qbit(b)*Num(1))],
                   [(Qbit(c)*Qbit(f)), (Qbit(g)*Num(2))]])

            Product of self and scalar value.

            >>> array_a * 5
            Array([[(Qbit(a)*Num(5)), (Qbit(b)*Num(5))],
                   [(Qbit(c)*Num(5)), 10]])

            Product of self and numpy ndarray.
            
            >>> array_a * np.array([[1, 2], [3, 4]])
            Array([[(Qbit(a)*Num(1)), (Qbit(b)*Num(2))],
                   [(Qbit(c)*Num(3)), 8]])
        """
        return self._pairwise_op_with_type_check(other, lambda x, y: x * y)

    @staticmethod
    @vartype_argument('vartype')
    def create(name, shape, vartype):
        """Create a new array with Spins or Qbits.

        Args:
            name (str): Name of the matrix. It is used as a part of the label of variables.
                For example, if the name is 'x',
                the label of `(i, j)` th variable will be ``x[i][j]``.
            
            shape (int/tuple[int]): Dimension of the array.
            
            vartype (:class:`dimod.Vartype`/str/set, optional):
                Variable type of the solution.
                Accepted input values:
                
                * :class:`.Vartype.SPIN`, ``'SPIN'``, ``{-1, 1}``
                * :class:`.Vartype.BINARY`, ``'BINARY'``, ``{0, 1}``

        Example:
            >>> from pyqubo import Array
            >>> array = Array.create('x', shape=(2, 2), vartype='BINARY')
            >>> array
            Array([[Qbit(x[0][0]), Qbit(x[0][1])],
                   [Qbit(x[1][0]), Qbit(x[1][1])]])
            >>> array[0]
            Array([Qbit(x[0][0]), Qbit(x[0][1])])
        """

        if isinstance(shape, int):
            shape = shape,

        if vartype == dimod.BINARY:
            var_class = Qbit
        else:
            var_class = Spin

        def var_name(name, index):
            return "{name}{index_repr}".format(
                name=name, index_repr=''.join(['[%d]' % i for i in index]))

        def create_structure(index):
            return {var_name(name, index): tuple([name] + index)}

        def generator(index):
            return var_class(var_name(name, index), create_structure(index))

        return Array._create_with_generator(shape, generator)

    @staticmethod
    def fill(obj, shape):
        """Create a new array with the given shape, all filled with the given object.
        
        Args:
            obj (int/float/:class:`Express`): The object with which a new array is filled. 
            shape (tuple[int]): Shape of the array. 
        
        Returns:
            :class:`Array`: Created array.
        
        Example:
            
            >>> from pyqubo import Array, Qbit
            >>> Array.fill(Qbit('a'), shape=(2, 3))
            Array([[Qbit(a), Qbit(a), Qbit(a)],
                   [Qbit(a), Qbit(a), Qbit(a)]])
        """
        return Array._create_with_generator(shape, lambda _: obj)

    @staticmethod
    def _create_with_generator(shape, generator):
        """Returns an array with objects which `generator` created.
        
        Args:
            shape (tuple[int]): Shape of the array.
            generator (list[int] =>:class:`Express`): Function to generate :class:`Express`:.
                Type of the argument of the generator is ``list[int]``.
        
        Returns:
            :class:`Array`: Created array.
        """

        _shape_list = list(shape)

        def create_internal(shape_list, index):
            if len(shape_list) > 1:
                length = shape_list[0]
                return [create_internal(shape_list[1:], index + [i]) for i in range(length)]
            else:
                length = shape_list[0]
                return [generator(index+[i]) for i in range(length)]

        return Array(create_internal(_shape_list, []))

    def _pairwise_op_with_type_check(self, other, operation):
        """Pairwise operation with type check.
        
        Args:
            other (:class:`Array`/:class:`ndarray`/int/float): The other object in operation.
            operation (:class:`Express`, :class:`Express` => :class:`Express`): Operation.
        
        Returns:
            :class:`Array`
        """
        if isinstance(other, np.ndarray):
            other = Array(other)
        elif isinstance(other, int) or isinstance(other, float) or isinstance(other, Express):
            other = Array.fill(other, self.shape)
        elif not isinstance(other, Array):
            raise TypeError('Operation of Array cannot be done with type:{type}'
                            .format(type=type(other)))
        return self._pairwise_op(other, operation)

    def _pairwise_op(self, other, operation):
        """Pairwise operation
        
        Args:
            other (:class:`Array`): The other object in operation.
            operation (:class:`Express`, :class:`Express` => :class:`Express`): Operation
        
        Returns:
            :class:`Array`
        """
        if not isinstance(other, Array): # pragma: no cover
            raise TypeError('Type of `other` is not a `Array` instance.')
        elif not self.shape == other.shape:
            raise ValueError('Shape of other is not same as that of self.')
        else:
            def operate(l1, l2):
                if isinstance(l1, list):
                    return [operate(e1, e2) for e1, e2 in zip(l1, l2)]
                else:
                    return operation(l1, l2)
            return Array(operate(self.bit_list, other.bit_list))

    @property
    def T(self):
        """Returns a transposed array.
        
        Example:
            >>> array = Array.create('x', shape=(2, 3), vartype='BINARY')
            >>> array
            Array([[Qbit(x[0][0]), Qbit(x[0][1]), Qbit(x[0][2])],
                   [Qbit(x[1][0]), Qbit(x[1][1]), Qbit(x[1][2])]])
            >>> array.T
            Array([[Qbit(x[0][0]), Qbit(x[1][0])],
                   [Qbit(x[0][1]), Qbit(x[1][1])],
                   [Qbit(x[0][2]), Qbit(x[1][2])]])
        """

        def generator(index):
            return self[tuple(index[::-1])]

        return Array._create_with_generator(self.shape[::-1], generator)

    def dot(self, other):
        """Returns a dot product of two arrays.
        
        Args:
            other (:class:`Array`): Array.
        
        Returns:
            :class:`Express`/:class:`Array`
        
        Example:
            
            Dot calculation falls into four patterns.
            
            1. If both `self` and `other` are 1-D arrays, it is inner product of vectors.
            
            >>> from pyqubo import Array, Qbit
            >>> array_a = Array([Qbit('a'), Qbit('b')])
            >>> array_b = Array([Qbit('c'), Qbit('d')])
            >>> array_a.dot(array_b)
            ((Qbit(a)*Qbit(c))+(Qbit(b)*Qbit(d)))
            
            2. If `self` is an N-D array and `other` is a 1-D array,\
                it is a sum product over the last axis of `self` and `other`.
            
            >>> array_a = Array([[Qbit('a'), Qbit('b')], [Qbit('c'), Qbit('d')]])
            >>> array_b = Array([Qbit('e'), Qbit('f')])
            >>> array_a.dot(array_b)
            Array([((Qbit(a)*Qbit(e))+(Qbit(b)*Qbit(f))), ((Qbit(c)*Qbit(e))+(Qbit(d)*Qbit(f)))])
            
            3. If both `self` and `other` are 2-D arrays, it is matrix multiplication.
            
            >>> array_a = Array([[Qbit('a'), Qbit('b')], [Qbit('c'), Qbit('d')]])
            >>> array_b = Array([[Qbit('e'), Qbit('f')], [Qbit('g'), Qbit('h')]])
            >>> array_a.dot(array_b)
            Array([[((Qbit(a)*Qbit(e))+(Qbit(b)*Qbit(g))), ((Qbit(a)*Qbit(f))+(Qbit(b)*Qbit(h)))],
                   [((Qbit(c)*Qbit(e))+(Qbit(d)*Qbit(g))), ((Qbit(c)*Qbit(f))+(Qbit(d)*Qbit(h)))]])
            
            4. If `self` is an N-D array and `other` is an M-D array (where N, M>=2),\
                it is a sum product over the last axis of `self` and\
                the second-to-last axis of `other`. If N = M = 3,\
                (i, j, k, m) element of a dot product of `self` and `other` is:

            .. code-block:: python

                dot(self, other)[i,j,k,m] = sum(self[i,j,:] * other[k,:,m])

            >>> array_a = Array.create('a', shape=(3, 2, 4), vartype='BINARY')
            >>> array_a.shape
            (3, 2, 4)
            >>> array_b = Array.create('b', shape=(5, 4, 3), vartype='BINARY')
            >>> array_b.shape
            (5, 4, 3)
            >>> i, j, k, m = (1, 1, 3, 2)
            >>> array_a.dot(array_b)[i, j, k, m] == sum(array_a[i, j, :] * array_b[k, :, m])
            True
            
            Dot product with list.
            
            >>> array_a = Array([Qbit('a'), Qbit('b')])
            >>> array_b = [3, 4]
            >>> array_a.dot(array_b)
            ((Qbit(a)*Num(3))+(Qbit(b)*Num(4)))
        """
        if isinstance(other, np.ndarray) or isinstance(other, list):
            other = Array(other)

        if not isinstance(other, Array):
            raise TypeError("Type of argument should be Array")

        # pattern 1 (see docstring)
        if len(self.shape) == 1 and len(other.shape) == 1 and self.shape[0] == other.shape[0]:
            return sum(self.mul(other))

        # pattern 2
        elif len(self.shape) == 2 and len(other.shape) == 1:
            return Array([sum(v * other) for v in self])

        # pattern 3 and 4
        else:
            return self._dot_matrix(other)

    def _dot_matrix(self, other):
        """Returns a dot product of N-D array self and M-D array other (where N, M>=2).
        """
        assert isinstance(other, Array), "Type should be Array, not {type}".format(type=type(other))
        assert self.shape[-1] == other.shape[-2],\
            "self.shape[-1] should be equal other.shape[-2].\n" +\
            "For more details, see https://pyqubo.readthedocs.io/en/latest/reference/array.html"

        vector_indices = slice(0, self.shape[-1], None)
        new_shape = self.shape[:-1] + other.shape[:-2] + (other.shape[-1],)

        def generator(index):
            half = len(self.shape) - 1
            index_self = tuple(index[:half]) + (vector_indices,)
            index_other = tuple(index[half:-1]) + (vector_indices,) + (index[-1],)
            vector_self = self[index_self]
            vector_other = other[index_other]
            return sum(vector_self * vector_other)

        return Array._create_with_generator(new_shape, generator)
