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

import dimod
import numpy as np


def solve_qubo(qubo, num_reads=10, num_sweeps=1000, beta_range=(1.0, 50.0)):
    """Solve QUBO with Simulated Annealing (SA) provided by dimod.
    
    Args:
        qubo (dict[(label, label), float]): The QUBO to be solved.
        
        num_reads (int, default=10): Number of run repetitions of SA.
        
        num_sweeps (int, default=1000): Number of iterations in each run of SA.
         
        beta_range (tuple(float, float), default=(1.0, 50.0)): Tuple of start beta and end beta.
         
    Returns:
         dict[label, bit]: The solution of SA.
    """
    max_abs_value = float(max(abs(v) for v in qubo.values()))
    scale_qubo = {k: float(v) / max_abs_value for k, v in qubo.items()}
    sa = dimod.reference.SimulatedAnnealingSampler()
    sa_computation = sa.sample_qubo(scale_qubo, num_reads=num_reads,
                                    num_sweeps=num_sweeps, beta_range=beta_range)
    best = np.argmin(sa_computation.record.energy)
    best_solution = list(sa_computation.record.sample[best])
    return dict(zip(sa_computation.variable_labels, best_solution))


def solve_ising(linear, quad, num_reads=10, num_sweeps=1000, beta_range=(1.0, 50.0)):
    """Solve Ising model with Simulated Annealing (SA) provided by dimod.

    Args:
        linear (dict[label, float]): The linear parameter of the Ising model.
        
        quad (dict[(label, label), float]): The quadratic parameter of the Ising model.

        num_reads (int, default=10): Number of run repetitions of SA.

        num_sweeps (int, default=1000): Number of iterations in each run of SA.

        beta_range (tuple(float, float), default=(1.0, 50.0)): Tuple of start beta and end beta.

    Returns:
         dict[label, bit]: The solution of SA.
    """
    max_abs_value = float(max(abs(v) for v in (list(quad.values()) + list(linear.values()))))
    scale_linear = {k: float(v) / max_abs_value for k, v in linear.items()}
    scale_quad = {k: float(v) / max_abs_value for k, v in quad.items()}
    sa = dimod.reference.SimulatedAnnealingSampler()
    sa_computation = sa.sample_ising(scale_linear, scale_quad, num_reads=num_reads,
                                     num_sweeps=num_sweeps, beta_range=beta_range)
    best = np.argmin(sa_computation.record.energy)
    best_solution = list(sa_computation.record.sample[best])
    return dict(zip(sa_computation.variable_labels, best_solution))
