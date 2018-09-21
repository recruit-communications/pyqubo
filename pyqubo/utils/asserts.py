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


def assert_qubo_equal(qubo1, qubo2):
    """ Assert the given QUBOs are identical.
    
    Args:
        qubo1 (dict[(label, label), float]): QUBO to be compared.
        
        qubo2 (dict[(label, label), float]): QUBO to be compared.
    """

    msg = "QUBO should be an dict instance."
    assert isinstance(qubo1, dict), msg
    assert isinstance(qubo2, dict), msg

    assert len(qubo1) == len(qubo2), "Number of elements in QUBO doesn't match."

    for (label1, label2), value in qubo1.items():
        if (label1, label2) in qubo2:
            if qubo2[label1, label2] != value:
                assert qubo2[label1, label2] == value,\
                    "Value of {key} doesn't match".format(key=(label1, label2))
        elif (label2, label1) in qubo2:
            if qubo2[label2, label1] != value:
                assert qubo2[label2, label1] == value, \
                    "Value of {key} doesn't match".format(key=(label2, label1))
        else:
            raise AssertionError("Key: {key} of qubo1 isn't contained in qubo2"
                                 .format(key=(label1, label2)))
