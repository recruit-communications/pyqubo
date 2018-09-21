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
    """The value of QUBO as a function of :class:`Param`.
    
    Energy of QUBO is defined as :math:`E(\\mathbf{x}) = \\sum_{ij} a_{ij}x_{i}x_{j}`.
    
    If the expression contains :class:`Param`, QUBO in :class:`Model` is `half-compiled`.
    `Half-compiled` means you need to specify the value of parameters to get the final QUBO.
    Each coefficient :math:`a_{ij}` of half-compiled QUBO is defined as :class:`Coefficient`.
    If you want to get the final value of :math:`a_{ij}`, you need to evaluate with `params`.
    
    Args:
        terms (dict[:class:`ParamProd`, float]): polynomial function of :class:`Param`.
            The labels in :class:`ParamProd` corresponds to labels of :class:`Param`.
            
    Example:
        
        For example, a polynomial :math:`2ab+2` is represented as
        
        >>> from pyqubo import Coefficient, ParamProd
        >>> coeff = Coefficient({ParamProd({'a': 1, 'b': 1}): 2.0, ParamProd({}): 2.0})
        
        If we specify the params as :math:`a=2, b=3`, then the evaluated value will be 14.0.
        
        >>> coeff.eval(params={'a': 2, 'b': 3})
        14.0
        
    """

    def __init__(self, terms):
        self.terms = terms

    def eval(self, params):
        """Returns evaluated value with `params`.
        
        Args:
            params (dict[str, float]): Parameters.
        
        Returns:
            float
        """
        if not params:
            raise ValueError("No parameters are given. Specify the parameter.")
        result = 0.0
        for term, value in self.terms.items():
            prod = value
            for key, p in term.keys.items():
                if key in params:
                    prod *= params[key] ** p
                else:
                    raise ValueError("{key} is not specified in params. "
                                     "Set the value of {key}".format(key=key))
            result += prod
        return result
