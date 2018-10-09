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


class Coefficient:
    """The value of QUBO as a function of :class:`Placeholder`.
    
    Energy of QUBO is defined as :math:`E(\\mathbf{x}) = \\sum_{ij} a_{ij}x_{i}x_{j}`.
    
    If the expression contains :class:`Placeholder`,
    you need to specify the value of placeholders to get the final QUBO.
    Each coefficient :math:`a_{ij}` of compiled QUBO is defined as :class:`Coefficient`.
    If you want to get the final value of :math:`a_{ij}`, you need to evaluate it with `feed_dict`.
    
    Args:
        terms (dict[:class:`PlaceholderProd`, float]): polynomial function of :class:`Placeholder`.
            The labels in :class:`PlaceholderProd` corresponds to labels of :class:`Placeholder`.
    
    Example:
        
        For example, a polynomial :math:`2ab+2` is represented as
        
        >>> from pyqubo import Coefficient, PlaceholderProd
        >>> coeff = Coefficient({PlaceholderProd({'a': 1, 'b': 1}): 2.0, PlaceholderProd({}): 2.0})
        
        If we specify the value of Placeholder as :math:`a=2, b=3`,
        then the evaluated value will be 14.0.
        
        >>> coeff.evaluate(feed_dict={'a': 2, 'b': 3})
        14.0
        
    """

    def __init__(self, terms):
        self.terms = terms

    def evaluate(self, feed_dict):
        """Returns evaluated value with `feed_dict`.
        
        Args:
            feed_dict (dict[str, float]): The value of placeholder.
        
        Returns:
            float
        """
        if not feed_dict:
            raise ValueError("No feed_dict are given. Specify the feed_dict.")
        result = 0.0
        for term, value in self.terms.items():
            prod = value
            for key, p in term.keys.items():
                if key in feed_dict:
                    prod *= feed_dict[key] ** p
                else:
                    raise ValueError("{key} is not specified in feed_dict. "
                                     "Set the value of {key}".format(key=key))
            result += prod
        return result
