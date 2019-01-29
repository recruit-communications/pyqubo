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
import six


@six.add_metaclass(abc.ABCMeta)
class Integer(object):

    def __init__(self):
        pass

    @property
    @abc.abstractmethod
    def value(self):
        pass

    @property
    @abc.abstractmethod
    def num_bits(self):
        """
        Returns number of bits used to represent integer.
        
        Returns:
             int
        """
        pass

    @property
    @abc.abstractmethod
    def interval(self):
        """
        Returns interval of integer.
        
        Returns:
            (int, int): Tuple of minimum value and maximum value.
        """
        pass
