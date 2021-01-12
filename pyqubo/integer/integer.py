# Copyright 2020 Recruit Communications Co., Ltd.
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
from cpp_pyqubo import UserDefinedExpress, WithPenalty


class Integer(UserDefinedExpress):
    """Binary encoded integer
    """

    def __init__(self, label, value_range, express):
        self.label=label
        self.value_range = value_range
        super().__init__(express)
    
    def __str__(self):
        return "{}({},value_range={})".format(self.__class__.__name__, self.label, self.value_range)

    def __repr__(self):
        return self.__str__()

class IntegerWithPenalty(WithPenalty):
    """Binary encoded integer with penalty function
    """

    def __init__(self, label, value_range, express, penalty):
        self.label=label
        self.value_range = value_range
        super().__init__(express, penalty, label)
    
    def __str__(self):
        return "{}({},value_range={})".format(self.__class__.__name__, self.label, self.value_range)

    def __repr__(self):
        return self.__str__()
