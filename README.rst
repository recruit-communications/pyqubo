.. image:: https://img.shields.io/pypi/v/pyqubo.svg
    :target: https://pypi.python.org/pypi/pyqubo

.. image:: https://codecov.io/gh/recruit-communications/pyqubo/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/recruit-communications/pyqubo

.. image:: https://readthedocs.org/projects/pyqubo/badge/?version=latest
    :target: http://pyqubo.readthedocs.io/en/latest/?badge=latest

.. image:: https://circleci.com/gh/recruit-communications/pyqubo.svg?style=svg
    :target: https://circleci.com/gh/recruit-communications/pyqubo

.. image:: https://pepy.tech/badge/pyqubo
    :target: https://pepy.tech/project/pyqubo

.. index-start-marker1

PyQUBO
======

PyQUBO allows you to create QUBOs or Ising models from flexible mathematical expressions easily.
Some of the features of PyQUBO are

* **Python based (C++ backend).**
* **Fully integrated with Ocean SDK.** (`details <https://github.com/recruit-communications/pyqubo#integration-with-d-wave-ocean>`__)
* **Automatic validation of constraints.** (`details <https://pyqubo.readthedocs.io/en/latest/getting_started.html#validation-of-constraints>`__)
* **Placeholder** for parameter tuning. (`details <https://pyqubo.readthedocs.io/en/latest/getting_started.html#placeholder>`__)


For more details, see `PyQUBO Documentation <https://pyqubo.readthedocs.io/>`_.

Example Usage
-------------

Creating QUBO
`````````````

This example constructs a simple expression and compile it to ``model``.
By calling ``model.to_qubo()``, we get the resulting QUBO.
(This example solves `Number Partitioning Problem <https://en.wikipedia.org/wiki/Partition_problem>`_ with a set S = {4, 2, 7, 1})

>>> from pyqubo import Spin
>>> s1, s2, s3, s4 = Spin("s1"), Spin("s2"), Spin("s3"), Spin("s4")
>>> H = (4*s1 + 2*s2 + 7*s3 + s4)**2
>>> model = H.compile()
>>> qubo, offset = model.to_qubo()
>>> pprint(qubo)
{('s1', 's1'): -160.0,
('s1', 's2'): 64.0,
('s2', 's2'): -96.0,
('s3', 's1'): 224.0,
('s3', 's2'): 112.0,
('s3', 's3'): -196.0,
('s4', 's1'): 32.0,
('s4', 's2'): 16.0,
('s4', 's3'): 56.0,
('s4', 's4'): -52.0}

.. _integration:

Integration with D-Wave Ocean
`````````````````````````````

PyQUBO can output the `BinaryQuadraticModel(BQM) <https://docs.ocean.dwavesys.com/en/stable/docs_dimod/reference/bqm.html>`_
which is compatible with `Sampler` class defined in D-Wave Ocean SDK.
In the example below, we solve the problem with `SimulatedAnnealingSampler`.

>>> import neal
>>> sampler = neal.SimulatedAnnealingSampler()
>>> bqm = model.to_bqm()
>>> sampleset = sampler.sample(bqm, num_reads=10)
>>> decoded_samples = model.decode_sampleset(sampleset)
>>> best_sample = min(decoded_samples, key=lambda x: x.energy)
>>> best_sample.sample # doctest: +SKIP
{'s1': 0, 's2': 0, 's3': 1, 's4': 0}

If you want to solve the problem by actual D-Wave machines,
just replace the `sampler` by a `DWaveCliqueSampler` instance, for example.


For more examples, see `example notebooks <https://github.com/recruit-communications/pyqubo/tree/master/notebooks>`_.


Benchmarking
------------

Since the core logic of the new PyQUBO (>=1.0.0) is written in C++ and the logic itself is also optimized, the execution time to produce QUBO has become shorter.
We benchmarked the execution time to produce QUBOs of TSP with the new PyQUBO (1.0.0) and the previous PyQUBO (0.4.0).
The result shows the new PyQUBO runs 1000 times faster as the problem size increases.

.. image:: https://raw.githubusercontent.com/recruit-communications/pyqubo/master/images/benchmark.svg
   :scale: 60%
   :width: 550
   :height: 440
   :align: center

Execution time includes building Hamiltonian, compilation, and producing QUBOs. The code to produce the above result is found in `here <https://github.com/recruit-communications/pyqubo/tree/master/benchmark/>`_.


Installation
------------

.. code-block:: shell

    pip install pyqubo

or

.. code-block:: shell

    python setup.py install

Supported Python Versions
-------------------------

Python 3.5, 3.6, 3.7 and 3.8 are supported.

Supported Operating Systems
---------------------------

- Linux (32/64bit)
- OSX (64bit, >=10.9)
- Win (64bit)

.. index-end-marker1

Test
----

Run all tests.

.. code-block:: shell

    python -m unittest discover test

Show coverage report.

.. code-block:: shell

    coverage run -m unittest discover
    coverage html

Run test with circleci CLI.

.. code-block:: shell

    circleci build --job $JOBNAME

Run doctest.

.. code-block:: shell

    make doctest


Dependency
----------

This repository contains the source code of `cimod <https://github.com/OpenJij/cimod>`_ which is licensed under the Apache License 2.0.
`cimod <https://github.com/OpenJij/cimod>`_ is the C++ header-only library for a binary quadratic model, developed by `OpenJij <https://github.com/OpenJij>`_.

Citation
--------

If you use PyQUBO in your research, please cite `this paper <https://journals.jps.jp/doi/full/10.7566/JPSJ.88.061010>`_.

::

    @article{tanahashi2019application,
      title={Application of Ising Machines and a Software Development for Ising Machines},
      author={Tanahashi, Kotaro and Takayanagi, Shinichi and Motohashi, Tomomitsu and Tanaka, Shu},
      journal={Journal of the Physical Society of Japan},
      volume={88},
      number={6},
      pages={061010},
      year={2019},
      publisher={The Physical Society of Japan}
    }


Organization
------------

Recruit Communications Co., Ltd.

Licence
-------

Released under the Apache License 2.0.

Contribution
------------

We welcome contributions to this project. See `CONTRIBUTING <./CONTRIBUTING.rst>`_.
