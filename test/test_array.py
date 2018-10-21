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
from pyqubo import Qbit, Spin, Array

import numpy as np


class TestArray(unittest.TestCase):

    def test_array_from_list(self):
        array = Array([[Qbit('x0'), Qbit('x1')], [Qbit('x2'), Qbit('x3')]])
        self.assertTrue(array.shape == (2, 2))
        self.assertTrue(array[0, 0] == Qbit('x0'))
        self.assertTrue(array[:, 0] == Array([Qbit('x0'), Qbit('x2')]))
        self.assertTrue(array[[0, 1], 0] == Array([Qbit('x0'), Qbit('x2')]))
        self.assertRaises(TypeError, lambda: Array(1))
        self.assertTrue(Array([[1, 2], [3, 4]]) == Array([Array([1, 2]), Array([3, 4])]))
        self.assertTrue(Array([[1, 2], [3, 4]]) == Array([np.array([1, 2]), np.array([3, 4])]))

    def test_array_error(self):
        # raise ValueError when the size of the sub lists is not same
        with self.assertRaises(ValueError):
            Array([[Qbit('x0'), Qbit('x1')], [Qbit('x2')]])

        # raise TypeError when index is neither int nor tuple[int]
        with self.assertRaises(TypeError):
            array = Array([Qbit('x0'), Qbit('x1')])
            array[1.5]

    def test_array_equality(self):
        array1 = Array([[Qbit('x0'), Qbit('x1')], [Qbit('x2'), Qbit('x3')]])
        array2 = Array([[Qbit('x0'), Qbit('x1')], [Qbit('x2'), Qbit('x3')]])
        array3 = Array([[Qbit('x0'), Qbit('x1')], [Qbit('x2'), Qbit('x4')]])
        self.assertTrue(array1 == array2)
        self.assertTrue(array1 != array3)
        self.assertTrue(not array1 == Qbit('x2'))

    def test_array_create_spin(self):
        array = Array.create('x', shape=(3, 3, 3), vartype='SPIN')
        self.assertTrue(array.shape == (3, 3, 3))
        self.assertTrue(array[0][0][0] == Spin('x[0][0][0]'))

    def test_array_create_binary(self):
        array = Array.create('x', shape=(3, 3, 3), vartype='BINARY')
        self.assertTrue(array.shape == (3, 3, 3))
        self.assertTrue(array[0][0][0] == Qbit('x[0][0][0]'))

    def test_array_repr(self):
        array = Array.create('x', shape=(3, 3, 3), vartype='BINARY')
        expected_string =\
            'Array([[[Qbit(x[0][0][0]), Qbit(x[0][0][1]), Qbit(x[0][0][2])],\n'\
            '        [Qbit(x[0][1][0]), Qbit(x[0][1][1]), Qbit(x[0][1][2])],\n'\
            '        [Qbit(x[0][2][0]), Qbit(x[0][2][1]), Qbit(x[0][2][2])]],\n'\
            '\n'\
            '       [[Qbit(x[1][0][0]), Qbit(x[1][0][1]), Qbit(x[1][0][2])],\n'\
            '        [Qbit(x[1][1][0]), Qbit(x[1][1][1]), Qbit(x[1][1][2])],\n'\
            '        [Qbit(x[1][2][0]), Qbit(x[1][2][1]), Qbit(x[1][2][2])]],\n'\
            '\n'\
            '       [[Qbit(x[2][0][0]), Qbit(x[2][0][1]), Qbit(x[2][0][2])],\n'\
            '        [Qbit(x[2][1][0]), Qbit(x[2][1][1]), Qbit(x[2][1][2])],\n'\
            '        [Qbit(x[2][2][0]), Qbit(x[2][2][1]), Qbit(x[2][2][2])]]])'
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
        expected = Array([[Qbit('x[0][0]'), Qbit('x[1][0]')],
                          [Qbit('x[0][1]'), Qbit('x[1][1]')],
                          [Qbit('x[0][2]'), Qbit('x[1][2]')]])
        self.assertTrue(array.T == expected)

    def test_array_add(self):
        array1 = Array.create('x', (2, 2), 'BINARY')
        array2 = Array.create('y', (2, 2), 'BINARY')
        expected = Array([[Qbit('x[0][0]') + Qbit('y[0][0]'), Qbit('x[0][1]') + Qbit('y[0][1]')],
                          [Qbit('x[1][0]') + Qbit('y[1][0]'), Qbit('x[1][1]') + Qbit('y[1][1]')]])
        self.assertTrue(array1 + array2 == expected)

        expected2 = Array([[Qbit('x[0][0]') + 1, Qbit('x[0][1]') + 1],
                          [Qbit('x[1][0]') + 1, Qbit('x[1][1]') + 1]])
        self.assertTrue(array1 + 1 == expected2)
        self.assertTrue(1 + array1 == expected2)
        self.assertTrue(array1 + np.ones((2, 2)) == expected2)

        self.assertRaises(TypeError, lambda: array1 + "str")
        array3 = Array.create('z', (2, 3), 'BINARY')
        self.assertRaises(ValueError, lambda: array1 + array3)

    def test_array_subtract(self):
        array1 = Array.create('x', (2, 2), 'BINARY')
        array2 = Array.create('y', (2, 2), 'BINARY')
        expected = Array([[Qbit('x[0][0]') - Qbit('y[0][0]'), Qbit('x[0][1]') - Qbit('y[0][1]')],
                          [Qbit('x[1][0]') - Qbit('y[1][0]'), Qbit('x[1][1]') - Qbit('y[1][1]')]])
        self.assertTrue(array1 - array2 == expected)

        expected2 = Array([[Qbit('x[0][0]') - 1, Qbit('x[0][1]') - 1],
                          [Qbit('x[1][0]') - 1, Qbit('x[1][1]') - 1]])
        self.assertTrue(array1 - 1 == expected2)
        expected3 = Array([[1 - Qbit('x[0][0]'), 1 - Qbit('x[0][1]')],
                           [1 - Qbit('x[1][0]'), 1 - Qbit('x[1][1]')]])
        self.assertTrue(1 - array1 == expected3)
        self.assertTrue(array1 - np.ones((2, 2)) == expected2)

    def test_array_multiply(self):
        array1 = Array.create('x', (2, 2), 'BINARY')
        array2 = Array.create('y', (2, 2), 'BINARY')
        expected = Array([[Qbit('x[0][0]') * Qbit('y[0][0]'), Qbit('x[0][1]') * Qbit('y[0][1]')],
                          [Qbit('x[1][0]') * Qbit('y[1][0]'), Qbit('x[1][1]') * Qbit('y[1][1]')]])
        self.assertTrue(array1 * array2 == expected)

        expected2 = Array([[Qbit('x[0][0]') * 2, Qbit('x[0][1]') * 2],
                           [Qbit('x[1][0]') * 2, Qbit('x[1][1]') * 2]])
        self.assertTrue(array1 * 2 == expected2)
        self.assertTrue(2 * array1 == expected2)
        self.assertTrue(array1 * (2*np.ones((2, 2))) == expected2)

    def test_array_division(self):
        array1 = Array.create('x', (2, 2), 'BINARY')
        expected = Array([[Qbit('x[0][0]') / 2.0, Qbit('x[0][1]') / 2.0],
                           [Qbit('x[1][0]') / 2.0, Qbit('x[1][1]') / 2.0]])
        self.assertTrue(array1 / 2.0 == expected)

        self.assertRaises(ValueError, lambda: 1 / array1)
        self.assertRaises(ValueError, lambda: array1 / array1)

    def test_array_dot(self):

        # inner product of 1-D arrays
        array_a = Array([Qbit('a'), Qbit('b')])
        array_b = Array([Qbit('c'), Qbit('d')])
        expected = ((Qbit('a') * Qbit('c')) + (Qbit('b') * Qbit('d')))
        self.assertTrue(expected == array_a.dot(array_b))

        # dot product of 1-D array and N-D array
        array_a = Array([[Qbit('a'), Qbit('b')], [Qbit('c'), Qbit('d')]])
        array_b = Array([Qbit('e'), Qbit('f')])
        expected = Array([((Qbit('a') * Qbit('e')) + (Qbit('b') * Qbit('f'))),
                          ((Qbit('c') * Qbit('e')) + (Qbit('d') * Qbit('f')))])
        self.assertTrue(expected == array_a.dot(array_b))

        # both are 2-D arrays
        array_a = Array([[Qbit('a'), Qbit('b')], [Qbit('c'), Qbit('d')]])
        array_b = Array([[Qbit('e'), Qbit('f')], [Qbit('g'), Qbit('h')]])
        expected = Array([[((Qbit('a') * Qbit('e')) + (Qbit('b') * Qbit('g'))),
                           ((Qbit('a') * Qbit('f')) + (Qbit('b') * Qbit('h')))],
                          [((Qbit('c') * Qbit('e')) + (Qbit('d') * Qbit('g'))),
                           ((Qbit('c') * Qbit('f')) + (Qbit('d') * Qbit('h')))]])
        self.assertTrue(expected == array_a.dot(array_b))

        # array_a is a  N-D array and array_b is an M-D array (where N, M>=2)
        array_a = Array.create('a', shape=(3, 2, 4), vartype='BINARY')
        array_b = Array.create('b', shape=(5, 4, 3), vartype='BINARY')
        i, j, k, m = (1, 1, 3, 2)
        self.assertTrue(array_a.dot(array_b)[i, j, k, m]
                        == sum(array_a[i, j, :] * array_b[k, :, m]))

        # dot with list
        array_a = Array([Qbit('a'), Qbit('b')])
        array_b = [3, 4]
        self.assertTrue((Qbit('a')*3 + (Qbit('b')*4)) == array_a.dot(array_b))

        # test exception
        self.assertRaises(TypeError, lambda: array_a.dot(1))
