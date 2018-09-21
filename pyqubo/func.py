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

from .core import UserDefinedExpress


class Sum(UserDefinedExpress):
    """Define sum of the expressions over sequent indices.
    
    Note:
        Indices run from :obj:`start_index` to :obj:`end_index-1`.

    Args:
        start_index (int): index to start with.
        
        end_index (int): index ends with end_index-1.
        
        func (function): function which takes integer as an argument and returns :class:`Express`.
    
    Example:
        >>> from pyqubo import Sum, Vector
        >>> x = Vector('x', n_dim=3)
        >>> exp = (Sum(0, 3, lambda i: x[i]) - 1.0)**2
        >>> pprint(exp.compile().to_qubo())
        ({('x[0]', 'x[0]'): -1.0,
          ('x[0]', 'x[1]'): 2.0,
          ('x[0]', 'x[2]'): 2.0,
          ('x[1]', 'x[1]'): -1.0,
          ('x[1]', 'x[2]'): 2.0,
          ('x[2]', 'x[2]'): -1.0},
         1.0)
    """

    def __init__(self, start_index, end_index, func):
        express = sum(func(i) for i in range(start_index, end_index))
        super(Sum, self).__init__(express)
