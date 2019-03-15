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

from operator import or_
import dimod
from six.moves import reduce


class CompiledQubo:
    """Compiled QUBO.

    Args:
        qubo (dict[label, :class:`Coefficient`/float]): QUBO
        offset (:class:`Coefficient`/float): Offset of QUBO

    Attributes:
        qubo (dict[label, :class:`Coefficient`/float]): QUBO
        offset (:class:`Coefficient`/float): Offset of QUBO

    This contains QUBO and the offset, but the value of the QUBO
    has not been evaluated yet. To get the final QUBO, you need to
    evaluate this QUBO by calling :func:`CompiledQubo.eval`.
    """

    def __init__(self, qubo, offset):
        self.qubo = qubo
        self.offset = offset

    @property
    def variables(self):
        """Unique labels contained in keys of QUBO."""
        return reduce(or_, [{i, j} for (i, j) in self.qubo.keys()])

    def evaluate(self, feed_dict):
        """Returns QUBO where the values are evaluated with feed_dict.

        Args:
            feed_dict (dict[str, float]): The value of :class:`Placeholder`.

        Returns:
            :class:`BinaryQuadraticModel`
        """
        evaluated_qubo = {}
        for k, v in self.qubo.items():
            evaluated_qubo[k] = CompiledQubo._eval_if_not_number(v, feed_dict)

        evaluated_offset = CompiledQubo._eval_if_not_number(self.offset, feed_dict)

        return dimod.BinaryQuadraticModel.from_qubo(
            evaluated_qubo, evaluated_offset)

    def __repr__(self):
        from pprint import pformat
        return "CompiledQubo({}, offset={})".format(pformat(self.qubo), self.offset)

    @staticmethod
    def _eval_if_not_number(v, feed_dict):
        """ If v is not float (i.e. v is :class:`Express`), returns an evaluated value.

        Args:
            v (float/int/:class:`Coefficient`):
                The value to be evaluated.
            feed_dict (dict[str, float]):
                The value of :class:`Placeholder`.

        Returns:
            float: Evaluated value of the input :obj:`v`:
        """
        if isinstance(v, float) or isinstance(v, int):
            return v
        else:
            return v.evaluate(feed_dict)
