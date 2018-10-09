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


class CompiledConstraint:
    """Compiled constraint.
    
    Args:
        polynomial (dict[:class:`BinaryProd`, float/:class:`Coefficient`]):
            Polynomial representation of constraint.
    """

    def __init__(self, polynomial):
        self.polynomial = polynomial

    def energy(self, binary_solution, feed_dict):
        """Returns the energy of constraint given a solution.
        
        Args:
            binary_solution (dict[label, bit]):
                Binary solution.

            feed_dict (dict[str, float]):
                The value of placeholders.
        
        Returns:
            float: Energy of constraint.
        """
        energy = 0.0
        for binary_prod, coeff in self.polynomial.items():
            evaluated_value = self._eval_if_not_float(coeff, feed_dict)
            energy += binary_prod.calc_product(binary_solution) * evaluated_value
        return energy

    @staticmethod
    def _eval_if_not_float(v, feed_dict):
        """If v is not float (i.e. v is :class:`Express`), returns an evaluated value.

        Args:
            v (float/:class:`Coefficient`):
                The value to be evaluated.

            feed_dict (dict[str, float]):
                The value of placeholders.

        Returns:
            float: Evaluated value of the input :obj:`v`:
        """
        if isinstance(v, float):
            return v
        else:
            return v.evaluate(feed_dict)
