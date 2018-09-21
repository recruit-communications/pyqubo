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

from .core import Spin, Qbit


class Matrix:
    """Matrix of variables.
    
    Args:
        name (str): Name of the matrix. It is used as a part of the label of variables.
            For example, if the matrix name is 'x',
            the label of `(i, j)` th variable will be ``x[i][j]``.
        
        n_row (int): Size of rows.
        
        n_col (int): Size of columns.
        
        spin (bool): If True, the element of the matrix is defined as :class:`Spin`.
        
    Examples:
        Create a binary matrix with a size of 2 * 3.
        
        >>> from pyqubo import Matrix
        >>> x = Matrix('x', 2, 3)
        >>> x[0, 1] + x[1, 2]
        (Qbit(x[0][1])+Qbit(x[1][2]))
    """

    def __init__(self, name, n_row, n_col, spin=False):
        self.n_row = n_row
        self.n_col = n_col
        self.name = name
        self.mat = {}
        structure = self._create_structure()
        for i in range(n_row):
            for j in range(n_col):
                if spin:
                    self.mat[(i, j)] = Spin(self._var_name(i, j), structure=structure)
                else:
                    self.mat[(i, j)] = Qbit(self._var_name(i, j), structure=structure)

    def __getitem__(self, key):
        i, j = key
        if i < 0 or j < 0 or i >= self.n_row or j >= self.n_col:
            raise IndexError
        return self.mat[(i, j)]

    def _var_name(self, i, j):
        return "{name}[{i}][{j}]".format(name=self.name, i=i, j=j)

    def _create_structure(self):
        structure = dict()
        for i in range(self.n_row):
            for j in range(self.n_col):
                structure[self._var_name(i, j)] = (self.name, i, j)
        return structure


class Vector:
    """Vector of variables.
    
    Args:
        name (str): Name of the vector. It is used as a part of the label of variables.
            For example, if the vector name is 'x', the label of `i` th variable will be ``x[i]``.
        
        n_dim (int): Size of the vector.
        
        spin (bool): If True, the element of the vector is defined as :class:`Spin`.
    
    Examples:
        Create a binary vector with a size of 3.
        
        >>> from pyqubo import Vector
        >>> x = Vector('x', 3)
        >>> x[0] + x[2]
        (Qbit(x[0])+Qbit(x[2]))
    """

    def __init__(self, name, n_dim, spin=False):
        self.n_dim = n_dim
        self.vec = {}
        self.name = name
        structure = self._create_structure()
        for i in range(n_dim):
            if spin:
                self.vec[i] = Spin(self._var_name(i), structure=structure)
            else:
                self.vec[i] = Qbit(self._var_name(i), structure=structure)

    def __getitem__(self, i):
        if i < 0 or i >= self.n_dim:
            raise IndexError
        return self.vec[i]

    def _var_name(self, i):
        return "{name}[{i}]".format(name=self.name, i=i)

    def _create_structure(self):
        structure = dict()
        for i in range(self.n_dim):
            structure[self._var_name(i)] = (self.name, i)
        return structure
