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

import unittest
from pyqubo import Binary, Spin, Array, Num

import numpy as np


class TestArray(unittest.TestCase):

    def test_array_from_list(self):
        array = Array([[Binary('x0'), Binary('x1')], [Binary('x2'), Binary('x3')]])
        self.assertTrue(array.shape == (2, 2))
        self.assertTrue(array[0, 0] == Binary('x0'))
        self.assertTrue(array[:, 0] == Array([Binary('x0'), Binary('x2')]))
        self.assertTrue(array[[0, 1], 0] == Array([Binary('x0'), Binary('x2')]))
        self.assertRaises(TypeError, lambda: Array(1))
        self.assertTrue(Array([[1, 2], [3, 4]]) == Array([Array([1, 2]), Array([3, 4])]))
        self.assertTrue(Array([[1, 2], [3, 4]]) == Array([np.array([1, 2]), np.array([3, 4])]))

    def test_array_error(self):
        # raise ValueError when the size of the sub lists is not same
        with self.assertRaises(ValueError):
            Array([[Binary('x0'), Binary('x1')], [Binary('x2')]])

        # raise TypeError when index is neither int nor tuple[int]
        with self.assertRaises(TypeError):
            array = Array([Binary('x0'), Binary('x1')])
            array[1.5]

    def test_array_equality(self):
        array1 = Array([[Binary('x0'), Binary('x1')], [Binary('x2'), Binary('x3')]])
        array2 = Array([[Binary('x0'), Binary('x1')], [Binary('x2'), Binary('x3')]])
        array3 = Array([[Binary('x0'), Binary('x1')], [Binary('x2'), Binary('x4')]])
        self.assertTrue(array1 == array2)
        self.assertTrue(array1 != array3)
        self.assertTrue(not array1 == Binary('x2'))

    def test_array_create_spin(self):
        array = Array.create('x', shape=(3, 3, 3), vartype='SPIN')
        self.assertTrue(array.shape == (3, 3, 3))
        self.assertTrue(array[0][0][0] == Spin('x[0][0][0]'))

    def test_array_create_binary(self):
        array = Array.create('x', shape=(3, 3, 3), vartype='BINARY')
        self.assertTrue(array.shape == (3, 3, 3))
        self.assertTrue(array[0][0][0] == Binary('x[0][0][0]'))

    def test_array_repr(self):
        array = Array.create('x', shape=(3, 3, 3), vartype='BINARY')
        expected_string =\
            'Array([[[Binary(x[0][0][0]), Binary(x[0][0][1]), Binary(x[0][0][2])],\n'\
            '        [Binary(x[0][1][0]), Binary(x[0][1][1]), Binary(x[0][1][2])],\n'\
            '        [Binary(x[0][2][0]), Binary(x[0][2][1]), Binary(x[0][2][2])]],\n'\
            '\n'\
            '       [[Binary(x[1][0][0]), Binary(x[1][0][1]), Binary(x[1][0][2])],\n'\
            '        [Binary(x[1][1][0]), Binary(x[1][1][1]), Binary(x[1][1][2])],\n'\
            '        [Binary(x[1][2][0]), Binary(x[1][2][1]), Binary(x[1][2][2])]],\n'\
            '\n'\
            '       [[Binary(x[2][0][0]), Binary(x[2][0][1]), Binary(x[2][0][2])],\n'\
            '        [Binary(x[2][1][0]), Binary(x[2][1][1]), Binary(x[2][1][2])],\n'\
            '        [Binary(x[2][2][0]), Binary(x[2][2][1]), Binary(x[2][2][2])]]])'
        self.assertTrue(repr(array) == expected_string)

    def test_array_iter(self):
        array = Array.create('x', shape=(2, 2), vartype='BINARY')
        self.assertTrue(len(array) == 2)
        self.assertTrue([e for e in array] == [array[0], array[1]])

    def test_array_from_numpy(self):
        array = Array(np.array([[1, 2], [3, 4]]))
        self.assertTrue(array == Array([[1, 2], [3, 4]]))

    def test_array_transpose(self):
        array = Array.create('x', (2, 3), 'BINARY')
        expected = Array([[Binary('x[0][0]'), Binary('x[1][0]')],
                          [Binary('x[0][1]'), Binary('x[1][1]')],
                          [Binary('x[0][2]'), Binary('x[1][2]')]])
        self.assertTrue(array.T == expected)

    def test_array_add(self):
        array1 = Array.create('x', (2, 2), 'BINARY')
        array2 = Array.create('y', (2, 2), 'BINARY')
        expected = Array([[Binary('x[0][0]') + Binary('y[0][0]'), Binary('x[0][1]') + Binary('y[0][1]')],
                          [Binary('x[1][0]') + Binary('y[1][0]'), Binary('x[1][1]') + Binary('y[1][1]')]])
        self.assertTrue(array1 + array2 == expected)

        expected2 = Array([[Binary('x[0][0]') + 1, Binary('x[0][1]') + 1],
                           [Binary('x[1][0]') + 1, Binary('x[1][1]') + 1]])
        self.assertTrue(array1 + 1 == expected2)
        self.assertTrue(1 + array1 == expected2)
        self.assertTrue(array1 + np.ones((2, 2)) == expected2)

        self.assertRaises(TypeError, lambda: array1 + "str")
        array3 = Array.create('z', (2, 3), 'BINARY')
        self.assertRaises(ValueError, lambda: array1 + array3)

    def test_array_subtract(self):
        array1 = Array.create('x', (2, 2), 'BINARY')
        array2 = Array.create('y', (2, 2), 'BINARY')
        expected = Array([[Binary('x[0][0]') - Binary('y[0][0]'), Binary('x[0][1]') - Binary('y[0][1]')],
                          [Binary('x[1][0]') - Binary('y[1][0]'), Binary('x[1][1]') - Binary('y[1][1]')]])
        self.assertTrue(array1 - array2 == expected)

        expected2 = Array([[Binary('x[0][0]') - 1, Binary('x[0][1]') - 1],
                           [Binary('x[1][0]') - 1, Binary('x[1][1]') - 1]])
        self.assertTrue(array1 - 1 == expected2)
        expected3 = Array([[1 - Binary('x[0][0]'), 1 - Binary('x[0][1]')],
                           [1 - Binary('x[1][0]'), 1 - Binary('x[1][1]')]])
        self.assertTrue(1 - array1 == expected3)
        self.assertTrue(array1 - np.ones((2, 2)) == expected2)

    def test_array_multiply(self):
        array1 = Array.create('x', (2, 2), 'BINARY')
        array2 = Array.create('y', (2, 2), 'BINARY')
        expected = Array([[Binary('x[0][0]') * Binary('y[0][0]'), Binary('x[0][1]') * Binary('y[0][1]')],
                          [Binary('x[1][0]') * Binary('y[1][0]'), Binary('x[1][1]') * Binary('y[1][1]')]])
        self.assertTrue(array1 * array2 == expected)

        expected2 = Array([[Binary('x[0][0]') * 2, Binary('x[0][1]') * 2],
                           [Binary('x[1][0]') * 2, Binary('x[1][1]') * 2]])
        self.assertTrue(array1 * 2 == expected2)
        self.assertTrue(2 * array1 == expected2)
        self.assertTrue(array1 * (2*np.ones((2, 2))) == expected2)

    def test_array_division(self):
        array1 = Array.create('x', (2, 2), 'BINARY')
        expected = Array([[Binary('x[0][0]') / 2.0, Binary('x[0][1]') / 2.0],
                          [Binary('x[1][0]') / 2.0, Binary('x[1][1]') / 2.0]])
        self.assertTrue(array1 / 2.0 == expected)

        self.assertRaises(ValueError, lambda: 1 / array1)
        self.assertRaises(ValueError, lambda: array1 / array1)

    def test_array_dot(self):

        # inner product of 1-D arrays
        array_a = Array([Binary('a'), Binary('b')])
        array_b = Array([Binary('c'), Binary('d')])
        expected = ((Binary('a') * Binary('c')) + (Binary('b') * Binary('d')))
        self.assertTrue(expected == array_a.dot(array_b))

        # dot product of 1-D array and N-D array
        array_a = Array([[Binary('a'), Binary('b')], [Binary('c'), Binary('d')]])
        array_b = Array([Binary('e'), Binary('f')])
        expected = Array([((Binary('a') * Binary('e')) + (Binary('b') * Binary('f'))),
                          ((Binary('c') * Binary('e')) + (Binary('d') * Binary('f')))])
        self.assertTrue(expected == array_a.dot(array_b))

        # both are 2-D arrays
        array_a = Array([[Binary('a'), Binary('b')], [Binary('c'), Binary('d')]])
        array_b = Array([[Binary('e'), Binary('f')], [Binary('g'), Binary('h')]])
        expected = Array([[((Binary('a') * Binary('e')) + (Binary('b') * Binary('g'))),
                           ((Binary('a') * Binary('f')) + (Binary('b') * Binary('h')))],
                          [((Binary('c') * Binary('e')) + (Binary('d') * Binary('g'))),
                           ((Binary('c') * Binary('f')) + (Binary('d') * Binary('h')))]])
        self.assertTrue(expected == array_a.dot(array_b))

        # array_a is a  N-D array and array_b is an M-D array (where N, M>=2)
        array_a = Array.create('a', shape=(3, 2, 4), vartype='BINARY')
        array_b = Array.create('b', shape=(5, 4, 3), vartype='BINARY')
        i, j, k, m = (1, 1, 3, 2)
        self.assertTrue(array_a.dot(array_b)[i, j, k, m]
                        == sum(array_a[i, j, :] * array_b[k, :, m]))

        # array_a is 1-D array and array_b is a list
        array_a = Array([Binary('a'), Binary('b')])
        array_b = [3, 4]
        self.assertTrue((Binary('a') * 3 + (Binary('b') * 4)) == array_a.dot(array_b))

        # test validation
        self.assertRaises(TypeError, lambda: array_a.dot(1))

    def test_array_matmul(self):

        # the either of the arguments is 1-D array,
        array_a = Array([[Binary('a'), Binary('b')], [Binary('c'), Binary('d')]])
        array_b = Array([Binary('e'), Binary('f')])
        expected = Array([((Binary('a') * Binary('e')) + (Binary('b') * Binary('f'))),
                          ((Binary('c') * Binary('e')) + (Binary('d') * Binary('f')))])
        self.assertTrue(array_a.matmul(array_b) == expected)

        # both arguments are 2-D array
        array_a = Array([[Binary('a'), Binary('b')], [Binary('c'), Binary('d')]])
        array_b = Array([[Binary('e'), Binary('f')], [Binary('g'), Binary('h')]])
        expected = Array([[((Binary('a') * Binary('e')) + (Binary('b') * Binary('g'))),
                           ((Binary('a') * Binary('f')) + (Binary('b') * Binary('h')))],
                          [((Binary('c') * Binary('e')) + (Binary('d') * Binary('g'))),
                           ((Binary('c') * Binary('f')) + (Binary('d') * Binary('h')))]])
        self.assertTrue(array_a.matmul(array_b) == expected)

        # either argument is N-D (where N > 2)
        array_a = Array.create('a', shape=(2, 2, 3), vartype='BINARY')
        array_b = Array.create('b', shape=(3, 2), vartype='BINARY')
        self.assertTrue((array_a.matmul(array_b))[0] == array_a[0].matmul(array_b))

        # array_a is 2-D array and array_b is a list
        array_a = Array([[Binary('a'), Binary('b')], [Binary('c'), Binary('d')]])
        array_b = [3, 4]
        expected = Array([((Binary('a') * Num(3)) + (Binary('b') * Num(4))), ((Binary('c') * Num(3)) + (Binary('d') * Num(4)))])
        self.assertTrue(expected == array_a.matmul(array_b))

        # test validation
        array_a = Array.create('a', shape=(2, 2, 3), vartype='BINARY')
        array_b = Array.create('b', shape=(3, 3, 2), vartype='BINARY')
        self.assertRaises(AssertionError, lambda: array_a.matmul(array_b))

    def test_array_reshape(self):
        array = Array.create('a', shape=(2, 3), vartype='BINARY')
        reshaped = array.reshape((3, 2))
        self.assertTrue(reshaped.shape == (3, 2))
        expected = Array([[Binary('a[0][0]'), Binary('a[0][1]')],
                          [Binary('a[0][2]'), Binary('a[1][0]')],
                          [Binary('a[1][1]'), Binary('a[1][2]')]])
        self.assertTrue(reshaped == expected)
