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

from cpp_pyqubo import Binary, Spin, Base

import dimod
from dimod.decorators import vartype_argument
import numpy as np
from operator import mul, add
from six.moves import reduce


class Array:
    """Multi-dimensional array.

    Args:
        bit_list (list/:class:`numpy.ndarray`): The object from which a new array is created.
            Accepted input:
        
                * (Nested) list of :class:`Express`, :class:`Array`, int or float.
                * numpy.ndarray

    Attributes:
        shape (tuple[int]): Shape of this array.

    Example:
        
        Create a new array with Binary.
        
        >>> from pyqubo import Array, Binary
        >>> Array.create('x', shape=(2, 2), vartype='BINARY')
        Array([[Binary(x[0][0]), Binary(x[0][1])],
               [Binary(x[1][0]), Binary(x[1][1])]])
        
        Create a new array from a nested list of :class:`Express`.
        
        >>> array = Array([[Binary('x0'), Binary('x1')], [Binary('x2'), Binary('x3')]])
        >>> array
        Array([[Binary(x0), Binary(x1)],
               [Binary(x2), Binary(x3)]])
        
        Get the shape of the array.
        
        >>> array.shape
        (2, 2)
        
        Access an element with index.
        
        >>> array[0, 0]  # = array[(0, 0)]
        Binary(x0)
        
        Use slice ":" to select a subset of the array.
        
        >>> array[:, 1]  # = array[(slice(None), 1)]
        Array([Binary(x1), Binary(x3)])
        >>> sum(array[:, 1])
        (Binary(x1)+Binary(x3))
        
        Use list or tuple to select a subset of the array.

        >>> array[[0, 1], 1]
        Array([Binary(x1), Binary(x3)])
        >>> array[(0, 1), 1]
        Array([Binary(x1), Binary(x3)])
        
        Create an array from numpy array.
        
        >>> import numpy as np
        >>> Array(np.array([[1, 2], [3, 4]]))
        Array([[1, 2],
               [3, 4]])
        
        Create an array from list of :class:`Array`.
        
        >>> Array([Array([1, 2]), Array([3, 4])])
        Array([[1, 2],
               [3, 4]])
    """

    def __init__(self, bit_list):

        if isinstance(bit_list, np.ndarray):
            self.shape = bit_list.shape
            self.bit_list = bit_list.tolist()

        elif isinstance(bit_list, list):
            def get_shape(l):
                if isinstance(l, list) or isinstance(l, Array) or isinstance(l, np.ndarray):
                    length = len(l)
                    shape_set = {get_shape(e) for e in l}
                    if len(shape_set) == 1:
                        sub_shape = shape_set.pop()
                        return tuple([length] + list(sub_shape))
                    else:
                        raise ValueError('Cannot determine the shape of input nested list.')
                else:
                    return tuple()

            def normalize_type(l):
                if isinstance(l, list):
                    return [normalize_type(e) for e in l]
                elif isinstance(l, Array):
                    return [normalize_type(e) for e in l.bit_list]
                elif isinstance(l, np.ndarray):
                    return [normalize_type(e) for e in l.tolist()]
                else:
                    return l

            self.shape = get_shape(bit_list)
            self.bit_list = normalize_type(bit_list)

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
            Array([[[Binary(x[0][0][0]), Binary(x[0][0][1])],
                    [Binary(x[0][1][0]), Binary(x[0][1][1])],
                    [Binary(x[0][2][0]), Binary(x[0][2][1])]],
            
                   [[Binary(x[1][0][0]), Binary(x[1][0][1])],
                    [Binary(x[1][1][0]), Binary(x[1][1][1])],
                    [Binary(x[1][2][0]), Binary(x[1][2][1])]]])
            >>> array[0, 1, 1]
            Binary(x[0][1][1])
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
        return self.div(other)

    def __rdiv__(self, other):
        """It is called when `other(number) / self`"""
        raise ValueError("Number cannot be divided by Expression.")

    def __truediv__(self, other):  # pragma: no cover
        """division in Python3"""
        return self.__div__(other)

    def __rtruediv__(self, other):  # pragma: no cover
        """It is called when `other(number) / self`"""
        return self.__rdiv__(other)

    def __matmul__(self, other):  # pragma: no cover
        return self.matmul(other)

    def add(self, other):
        """Returns a sum of self and other.
        
        Args:
            other (:class:`Array`/:class:`ndarray`/int/float): Addend.
        
        Returns:
            :class:`Array`
        
        Example:
            
            >>> from pyqubo import Array, Binary
            >>> import numpy as np
            >>> array_a = Array([[Binary('a'), Binary('b')], [Binary('c'), 2]])
            >>> array_b = Array([[Binary('d'), 1], [Binary('f'), Binary('g')]])
            >>> array_a.add(array_b) # doctest: +SKIP
            Array([[(Binary(a)+Binary(d)), (Binary(b)+Num(1))],
                   [(Binary(c)+Binary(f)), (Binary(g)+Num(2))]])
            >>> array_a + array_b # doctest: +SKIP
            Array([[(Binary(a)+Binary(d)), (Binary(b)+Num(1))],
                   [(Binary(c)+Binary(f)), (Binary(g)+Num(2))]])

            Sum of self and scalar value.
            
            >>> array_a + 5 # doctest: +SKIP
            Array([[(Binary(a)+Num(5)), (Binary(b)+Num(5))],
                   [(Binary(c)+Num(5)), 7]])
            
            Sum of self and numpy ndarray.
            
            >>> array_a + np.array([[1, 2], [3, 4]]) # doctest: +SKIP
            Array([[(Binary(a)+Num(1)), (Binary(b)+Num(2))],
                   [(Binary(c)+Num(3)), 6]])
        """
        return self._pairwise_op_with_type_check(other, lambda x, y: x + y)

    def subtract(self, other):
        """Returns a difference between other and self.

        Args:
            other (:class:`Array`/:class:`ndarray`/int/float): Subtrahend.

        Returns:
            :class:`Array`

        Example:

            >>> from pyqubo import Array, Binary
            >>> import numpy as np
            >>> array_a = Array([[Binary('a'), Binary('b')], [Binary('c'), 2]])
            >>> array_b = Array([[Binary('d'), 1], [Binary('f'), Binary('g')]])
            >>> array_a.subtract(array_b) # doctest: +SKIP
            Array([[(Binary(a)+(Binary(d)*Num(-1))), (Binary(b)+Num(-1))],
                   [(Binary(c)+(Binary(f)*Num(-1))), ((Binary(g)*Num(-1))+Num(2))]])
            >>> array_a - array_b # doctest: +SKIP
            Array([[(Binary(a)+(Binary(d)*Num(-1))), (Binary(b)+Num(-1))],
                   [(Binary(c)+(Binary(f)*Num(-1))), ((Binary(g)*Num(-1))+Num(2))]])

            Difference of self and scalar value.
            
            >>> array_a - 5 # doctest: +SKIP
            Array([[(Binary(a)+Num(-5)), (Binary(b)+Num(-5))],
                   [(Binary(c)+Num(-5)), -3]])
            
            Difference of self and numpy ndarray.
            
            >>> array_a - np.array([[1, 2], [3, 4]]) # doctest: +SKIP
            Array([[(Binary(a)+Num(-1)), (Binary(b)+Num(-2))],
                   [(Binary(c)+Num(-3)), -2]])
        """
        return self._pairwise_op_with_type_check(other, lambda x, y: x - y)

    def mul(self, other):
        """Returns a multiplicity of self by other.

        Args:
            other (:class:`Array`/:class:`ndarray`/int/float): Factor.

        Returns:
            :class:`Array`

        Example:

            >>> from pyqubo import Array, Binary
            >>> import numpy as np
            >>> array_a = Array([[Binary('a'), Binary('b')], [Binary('c'), 2]])
            >>> array_b = Array([[Binary('d'), 1], [Binary('f'), Binary('g')]])
            >>> array_a.mul(array_b) # doctest: +SKIP
            Array([[(Binary(a)*Binary(d)), (Binary(b)*Num(1))],
                   [(Binary(c)*Binary(f)), (Binary(g)*Num(2))]])
            >>> array_a * array_b # doctest: +SKIP
            Array([[(Binary(a)*Binary(d)), (Binary(b)*Num(1))],
                   [(Binary(c)*Binary(f)), (Binary(g)*Num(2))]])

            Product of self and scalar value.

            >>> array_a * 5 # doctest: +SKIP
            Array([[(Binary(a)*Num(5)), (Binary(b)*Num(5))],
                   [(Binary(c)*Num(5)), 10]])

            Product of self and numpy ndarray.
            
            >>> array_a * np.array([[1, 2], [3, 4]]) # doctest: +SKIP
            Array([[(Binary(a)*Num(1)), (Binary(b)*Num(2))],
                   [(Binary(c)*Num(3)), 8]])
        """
        return self._pairwise_op_with_type_check(other, lambda x, y: x * y)

    def div(self, other):
        """Returns division of self by other.
        
        Args:
            other (int/float): Divisor.
        
        Returns:
            :class:`Array`
        
        Example:
            
            >>> from pyqubo import Array, Binary
            >>> array_a = Array([[Binary('a'), Binary('b')], [Binary('c'), 2]])
            >>> array_a / 5 # doctest: +SKIP
            Array([[(Binary(a)*Num(0.2)), (Binary(b)*Num(0.2))],
                   [(Binary(c)*Num(0.2)), 0.4]])
        """
        if not isinstance(other, Array):
            return self * (other ** -1)
        else:
            raise ValueError("Expression cannot be divided by Expression.")

    @staticmethod
    @vartype_argument('vartype')
    def create(name, shape, vartype):
        """Create a new array with Spins or Binary.

        Args:
            name (str): Name of the matrix. It is used as a part of the label of variables.
                For example, if the name is 'x',
                the label of `(i, j)` th variable will be ``x[i][j]``.
            
            shape (int/tuple[int]): Dimensions of the array.
            
            vartype (:class:`dimod.Vartype`/str/set, optional):
                Variable type of the solution.
                Accepted input values:
                
                * :class:`.Vartype.SPIN`, ``'SPIN'``, ``{-1, 1}``
                * :class:`.Vartype.BINARY`, ``'BINARY'``, ``{0, 1}``

        Example:
            >>> from pyqubo import Array
            >>> array = Array.create('x', shape=(2, 2), vartype='BINARY')
            >>> array # doctest: +SKIP
            Array([[Binary(x[0][0]), Binary(x[0][1])],
                   [Binary(x[1][0]), Binary(x[1][1])]])
            >>> array[0] # doctest: +SKIP
            Array([Binary(x[0][0]), Binary(x[0][1])])
        """

        if isinstance(shape, int):
            shape = shape,

        if vartype == dimod.Vartype.BINARY:
            var_class = Binary
        else:
            var_class = Spin

        def var_name(_name, index):
            return "{name}{index_repr}".format(
                name=_name, index_repr=''.join(['[%d]' % i for i in index]))

        def create_structure(index):
            return {var_name(name, index): tuple([name] + index)}

        def generator(index):
            var_label = var_name(name, index)
            e = var_class(var_label)
            return e

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
            
            >>> from pyqubo import Array, Binary
            >>> Array.fill(Binary('a'), shape=(2, 3))
            Array([[Binary(a), Binary(a), Binary(a)],
                   [Binary(a), Binary(a), Binary(a)]])
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
        elif isinstance(other, int) or isinstance(other, float) or isinstance(other, Base):
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
        if not isinstance(other, Array):  # pragma: no cover
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
            >>> from pyqubo import Array
            >>> array = Array.create('x', shape=(2, 3), vartype='BINARY')
            >>> array
            Array([[Binary(x[0][0]), Binary(x[0][1]), Binary(x[0][2])],
                   [Binary(x[1][0]), Binary(x[1][1]), Binary(x[1][2])]])
            >>> array.T
            Array([[Binary(x[0][0]), Binary(x[1][0])],
                   [Binary(x[0][1]), Binary(x[1][1])],
                   [Binary(x[0][2]), Binary(x[1][2])]])
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
            
            >>> from pyqubo import Array, Binary
            >>> array_a = Array([Binary('a'), Binary('b')])
            >>> array_b = Array([Binary('c'), Binary('d')])
            >>> array_a.dot(array_b) # doctest: +SKIP
            ((Binary(a)*Binary(c))+(Binary(b)*Binary(d)))
            
            2. If `self` is an N-D array and `other` is a 1-D array,\
                it is a sum product over the last axis of `self` and `other`.
            
            >>> array_a = Array([[Binary('a'), Binary('b')], [Binary('c'), Binary('d')]])
            >>> array_b = Array([Binary('e'), Binary('f')])
            >>> array_a.dot(array_b) # doctest: +SKIP
            Array([((Binary(a)*Binary(e))+(Binary(b)*Binary(f))), \
                ((Binary(c)*Binary(e))+(Binary(d)*Binary(f)))])
            
            3. If both `self` and `other` are 2-D arrays, it is matrix multiplication.
            
            >>> array_a = Array([[Binary('a'), Binary('b')], [Binary('c'), Binary('d')]])
            >>> array_b = Array([[Binary('e'), Binary('f')], [Binary('g'), Binary('h')]])
            >>> array_a.dot(array_b) # doctest: +SKIP
            Array([[((Binary(a)*Binary(e))+(Binary(b)*Binary(g))), \
                ((Binary(a)*Binary(f))+(Binary(b)*Binary(h)))],
                   [((Binary(c)*Binary(e))+(Binary(d)*Binary(g))), \
                ((Binary(c)*Binary(f))+(Binary(d)*Binary(h)))]])
            
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
            
            >>> array_a = Array([Binary('a'), Binary('b')])
            >>> array_b = [3, 4]
            >>> array_a.dot(array_b) # doctest: +SKIP
            ((Binary(a)*Num(3))+(Binary(b)*Num(4)))
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

    def matmul(self, other):
        """Returns a matrix product of two arrays.
        
        Note:
            You can use operator symbol '@' instead of :obj:`matmul()`
            in Python 3.5 or later version.
        
        >>> from pyqubo import Array
        >>> array_a = Array.create('a', shape=(2, 4), vartype='BINARY')
        >>> array_b = Array.create('b', shape=(4, 3), vartype='BINARY')
        >>> array_a @ array_b == array_a.matmul(array_b)
        True
        
        Args:
            other (:class:`Array`/:class:`numpy.ndarray`/list): 
        
        Returns:
            :class:`Array`/:class:`Express`
        
        Example:
        
            Matrix product of two arrays falls into 3 patterns.
            
            1. If either of the arguments is 1-D array,
            it is treated as a matrix where one is added to its dimension.
            
            >>> from pyqubo import Array, Binary
            >>> array_a = Array([[Binary('a'), Binary('b')], [Binary('c'), Binary('d')]])
            >>> array_b = Array([Binary('e'), Binary('f')])
            >>> array_a.matmul(array_b) # doctest: +SKIP
            Array([((Binary(a)*Binary(e))+(Binary(b)*Binary(f))), \
                ((Binary(c)*Binary(e))+(Binary(d)*Binary(f)))])
            
            2. If both arguments are 2-D array, conventional matrix product is calculated.
            
            >>> array_a = Array([[Binary('a'), Binary('b')], [Binary('c'), Binary('d')]])
            >>> array_b = Array([[Binary('e'), Binary('f')], [Binary('g'), Binary('h')]])
            >>> array_a.matmul(array_b) # doctest: +SKIP
            Array([[((Binary(a)*Binary(e))+(Binary(b)*Binary(g))), \
                ((Binary(a)*Binary(f))+(Binary(b)*Binary(h)))],
                   [((Binary(c)*Binary(e))+(Binary(d)*Binary(g))), \
                ((Binary(c)*Binary(f))+(Binary(d)*Binary(h)))]])
            
            3. If either argument is N-D (where N > 2), it is treated as an array whose element is a
            2-D matrix of last two indices. In this example, `array_a` is treated as if
            it is a vector whose elements are two matrices of shape (2, 3).

            >>> array_a = Array.create('a', shape=(2, 2, 3), vartype='BINARY')
            >>> array_b = Array.create('b', shape=(3, 2), vartype='BINARY')
            >>> (array_a @ array_b)[0] == array_a[0].matmul(array_b)
            True
        """

        if isinstance(other, np.ndarray) or isinstance(other, list):
            other = Array(other)
        assert isinstance(other, Array), "Type should be Array, not {type}".format(type=type(other))

        # pattern 1 (see docstring)
        if len(self.shape) == 1 or len(other.shape) == 1:
            return self.dot(other)

        # pattern 2 and 3
        else:
            return self._matmul_matrix(other)

    def _matmul_matrix(self, other):

        assert isinstance(other, Array), "Type should be Array, not {type}".format(type=type(other))
        assert len(self.shape) >= 2 and len(other.shape) >= 2, "Shape should be greater than 2"
        assert self.shape[-1] == other.shape[-2], \
            "self.shape[-1] should be equal other.shape[-2].\n" + \
            "For more details, see https://pyqubo.readthedocs.io/en/latest/reference/array.html"

        self_shape_len = len(self.shape)
        other_shape_len = len(other.shape)

        common_len = min(self_shape_len, other_shape_len)

        for s1, s2 in zip(self.shape[-common_len:-2], other.shape[-common_len:-2]):
            assert s1 == s2, "Shape doesn't match."

        longer_shape = self.shape if self_shape_len > other_shape_len else other.shape
        new_shape = longer_shape[:-2] + (self.shape[-2], other.shape[-1])

        def generator(index):
            mat_index_self = tuple(index[-self_shape_len:][:-2])
            mat_index_other = tuple(index[-other_shape_len:][:-2])
            mat_self = self[mat_index_self] if mat_index_self != () else self
            mat_other = other[mat_index_other] if mat_index_other != () else other
            j = index[-1]
            i = index[-2]
            return mat_self[i, :].dot(mat_other[:, j])

        return Array._create_with_generator(new_shape, generator)

    @staticmethod
    def _calc_steps(shape):
        """Returns steps of shape.
        
        Step is used to create an 1-dim index from n-dim index like
        
        >>> steps = Array._calc_steps(shape)
        >>> one_dim_index = sum(step * i for step, i in zip(steps, n_dim_index))
        """
        steps = []
        tmp_d = 1
        for d in shape[::-1]:
            steps.append(tmp_d)
            tmp_d *= d
        steps = steps[::-1]
        return steps

    def reshape(self, new_shape):
        """Returns a reshaped array.
        
        Args:
            new_shape (tuple[int]): New shape.
        
        Example:
            
            >>> from pyqubo import Array
            >>> array = Array.create('x', shape=(2, 3), vartype='BINARY')
            >>> array
            Array([[Binary(x[0][0]), Binary(x[0][1]), Binary(x[0][2])],
                   [Binary(x[1][0]), Binary(x[1][1]), Binary(x[1][2])]])
            >>> array.reshape((3, 2, 1))
            Array([[[Binary(x[0][0])],
                    [Binary(x[0][1])]],\
            
                   [[Binary(x[0][2])],
                    [Binary(x[1][0])]],\

                   [[Binary(x[1][1])],
                    [Binary(x[1][2])]]])

        """
        assert reduce(mul, self.shape) == reduce(mul, new_shape),\
            "cannot reshape array of size {p} into shape {new_shape}".format(
                p=reduce(mul, self.shape), new_shape=new_shape)

        def calc_one_dim_array(nested_list):
            if isinstance(nested_list, list):
                return reduce(add, [calc_one_dim_array(e) for e in nested_list])
            else:
                return [nested_list]

        # create an 1-dim array from the n-dim array
        one_dim_array = calc_one_dim_array(self.bit_list)

        new_steps = Array._calc_steps(new_shape)

        def generator(index):
            # create an index for 1-dim array from the given index
            one_dim_index = sum(step * i for step, i in zip(new_steps, index))
            return one_dim_array[one_dim_index]

        return Array._create_with_generator(new_shape, generator)
