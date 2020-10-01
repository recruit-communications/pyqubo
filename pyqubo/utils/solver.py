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

import neal
import numpy as np
from deprecated import deprecated


@deprecated(version='0.4.0', reason="You should use simulated annealing sampler of dwave-neal directly.")
def solve_qubo(qubo, num_reads=10, sweeps=1000, beta_range=(1.0, 50.0)):
    """[deprecated] Solve QUBO with Simulated Annealing (SA) provided by neal.
    
    Args:
        qubo (dict[(label, label), float]): The QUBO to be solved.
        
        num_reads (int, default=10): Number of run repetitions of SA.
        
        sweeps (int, default=1000): Number of iterations in each run of SA.
         
        beta_range (tuple(float, float), default=(1.0, 50.0)): Tuple of start beta and end beta.
         
    Returns:
         dict[label, bit]: The solution of SA.
    
    Note:

        :func:`solve_qubo` is deprecated. Use `dwave-neal` package instead like below.

        >>> from pyqubo import Spin
        >>> import neal
        >>> s1, s2, s3 = Spin("s1"), Spin("s2"), Spin("s3")
        >>> H = (2*s1 + 4*s2 + 6*s3)**2
        >>> model = H.compile()
        >>> bqm = model.to_bqm()
        >>> sa = neal.SimulatedAnnealingSampler()
        >>> sampleset = sa.sample(bqm, num_reads=10)
        >>> samples = model.decode_sampleset(sampleset)
        >>> best_sample = min(samples, key=lambda s: s.energy)
        >>> pprint(best_sample.sample) # doctest: +SKIP
        {'s1': 0, 's2': 0, 's3': 1}

    """
    max_abs_value = float(max(abs(v) for v in qubo.values()))
    scale_qubo = {k: float(v) / max_abs_value for k, v in qubo.items()}
    sa = neal.SimulatedAnnealingSampler()
    sa_computation = sa.sample_qubo(scale_qubo, num_reads=num_reads,
                                    num_sweeps=sweeps, beta_range=beta_range)
    best = np.argmin(sa_computation.record.energy)
    best_solution = list(sa_computation.record.sample[best])
    return dict(zip(sa_computation.variables, best_solution))


@deprecated(version='0.4.0', reason="You should use simulated annealing sampler of dwave-neal directly.")
def solve_ising(linear, quad, num_reads=10, sweeps=1000, beta_range=(1.0, 50.0)):
    """[deprecated] Solve Ising model with Simulated Annealing (SA) provided by neal.

    Args:
        linear (dict[label, float]): The linear parameter of the Ising model.
        
        quad (dict[(label, label), float]): The quadratic parameter of the Ising model.

        num_reads (int, default=10): Number of run repetitions of SA.

        sweeps (int, default=1000): Number of iterations in each run of SA.

        beta_range (tuple(float, float), default=(1.0, 50.0)): Tuple of start beta and end beta.

    Note:

        :func:`solve_ising` is deprecated. Use `dwave-neal` package instead like below.

        >>> from pyqubo import Spin
        >>> import neal
        >>> s1, s2, s3 = Spin("s1"), Spin("s2"), Spin("s3")
        >>> H = (2*s1 + 4*s2 + 6*s3)**2
        >>> model = H.compile()
        >>> bqm = model.to_bqm()
        >>> sa = neal.SimulatedAnnealingSampler()
        >>> sampleset = sa.sample(bqm, num_reads=10)
        >>> samples = model.decode_sampleset(sampleset)
        >>> best_sample = min(samples, key=lambda s: s.energy)
        >>> pprint(best_sample.sample) # doctest: +SKIP
        {'s1': 0, 's2': 0, 's3': 1}
    """
    max_abs_value = float(max(abs(v) for v in (list(quad.values()) + list(linear.values()))))
    scale_linear = {k: float(v) / max_abs_value for k, v in linear.items()}
    scale_quad = {k: float(v) / max_abs_value for k, v in quad.items()}
    sa = neal.SimulatedAnnealingSampler()
    sa_computation = sa.sample_ising(scale_linear, scale_quad, num_reads=num_reads,
                                     num_sweeps=sweeps, beta_range=beta_range)
    best = np.argmin(sa_computation.record.energy)
    best_solution = list(sa_computation.record.sample[best])
    return dict(zip(sa_computation.variables, best_solution))
