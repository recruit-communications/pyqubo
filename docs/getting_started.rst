Getting Started
===============

Installation
------------

You can install PyQUBO using pip:

.. code-block:: shell

    pip install pyqubo

You can also install from the source code:

.. code-block:: shell

    git clone https://github.com/recruit-communications/pyqubo.git
    cd pyqubo
    python setup.py install


QUBO and Ising Model
--------------------

If you want to solve a combinatorial optimization problem using quantum or classical annealing machines, you need to represent your problem as a QUBO (Quadratic Unconstrained Binary Optimization) or Ising model. PyQUBO converts your problem into QUBO or Ising model format.

The objective function of the **QUBO** is defined as:

.. math::

    \sum_{i \le j}q_{ij}x_{i}x_{j}


where :math:`x_{i}` represents a binary variable which takes 0 or 1, and :math:`q_{ij}` represents a quadratic coefficient.
Note that :math:`q_{ii}x_{i}x_{i}=q_{ii}x_{i}`, since :math:`x_{i}^2=x_{i}`.
Thus, the above expression includes linear terms of :math:`x_{i}`.

The objective function of the **Ising model** is defined as:

.. math::

    \sum_{i}h_{i}s_{i} + \sum_{i<j}J_{ij}s_{i}s_{j}

where :math:`s_{i}` represents spin variable which takes -1 or 1, :math:`h_{i}` represents an external magnetic field and :math:`J_{ij}` represents an interaction between spin :math:`i` and :math:`j`.

Basic Usage
-----------

With PyQUBO, you can construct QUBOs with 3 steps:

1. **Define the hamiltonian.**

>>> from pyqubo import Spin
>>> s1, s2, s3, s4 = Spin("s1"), Spin("s2"), Spin("s3"), Spin("s4")
>>> H = (4*s1 + 2*s2 + 7*s3 + s4)**2

2. **Compile the hamiltonian to get a model.**

>>> model = H.compile()

3. **Call ‘to_qubo()’ to get QUBO coefficients.**

>>> qubo, offset = model.to_qubo()
>>> pprint(qubo) # doctest: +SKIP
{('s1', 's1'): -160.0,
 ('s1', 's2'): 64.0,
 ('s1', 's3'): 224.0,
 ('s1', 's4'): 32.0,
 ('s2', 's2'): -96.0,
 ('s2', 's3'): 112.0,
 ('s2', 's4'): 16.0,
 ('s3', 's3'): -196.0,
 ('s3', 's4'): 56.0,
 ('s4', 's4'): -52.0}
>>> print(offset)
196.0

In this example, we are solving the `Number Partitioning Problem <https://en.wikipedia.org/wiki/Partition_problem>`_ given the set :math:`S` = {4, 2, 7, 1}. The hamiltonian :math:`H` is represented as

.. math::

    H = (4 s_{1} + 2 s_{2} + 7 s_{3} + s_{4})^2

where :math:`s_{i}` is the :math:`i` -th spin variable, which indicates the group that the :math:`i` -th number should belong.
In PyQUBO, spin variables are internally converted to binary variables via the relationship :math:`x_{i} = (s_{i}+1)/2`. The QUBO coefficents and the offset returned from :obj:`Model.to_qubo()` represent the following objective function:

.. math::

    &-160 x_{1}x_{1} + 64 x_{1}x_{2} + 224 x_{1}x_{3} + 32 x_{1}x_{4} - 96 x_{2}x_{2}\\
    &+ 112 x_{2}x_{3} + 16 x_{2}x_{4} - 196 x_{3}x_{3} + 56 x_{3}x_{4} - 52 x_{4}x_{4} + 196


4. **Call ‘to_ising()’ to get Ising coefficients.**

To get the coefficient of the Ising model, just call the :obj:`Model.to_ising()` method, as demonstrated below.

>>> linear, quadratic, offset = model.to_ising()
>>> pprint(linear) # doctest: +SKIP
{'s1': 0.0, 's2': 0.0, 's3': 0.0, 's4': 0.0}
>>> pprint(quadratic) # doctest: +SKIP
{('s1', 's2'): 16.0,
 ('s1', 's3'): 56.0,
 ('s1', 's4'): 8.0,
 ('s2', 's3'): 28.0,
 ('s2', 's4'): 4.0,
 ('s3', 's4'): 14.0}
>>> print(offset)
70.0

`linear` represents external magnetic fields :math:`h`, `quadratic` represents interactions :math:`J`, and `offset` represents the constant value in the objective function below. 

.. math::

    16 s_{1}s_{2} + 56 s_{1}s_{3} + 8 s_{1}s_{4} + 28 s_{2}s_{3} + 4 s_{2}s_{4} + 14 s_{3}s_{4} + 70


Variable: Binary and Spin
-------------------------

When defining a hamiltonian, :class:`Binary` or :class:`Spin` can be used as a variable.

**Example:**
When defining a hamiltonian with binary variables :math:`x \in \{0, 1\}`, use :class:`Binary`.

>>> from pyqubo import Binary
>>> x1, x2 = Binary('x1'), Binary('x2')
>>> exp = 2*x1*x2 + 3*x1
>>> pprint(exp.compile().to_qubo()) # doctest: +SKIP
({('x1', 'x1'): 3.0, ('x1', 'x2'): 2.0, ('x2', 'x2'): 0.0}, 0.0)

**Example:**
When defining a hamiltonian with spin variables :math:`s \in \{-1, 1\}`, use :class:`Spin`.

>>> from pyqubo import Spin
>>> s1, s2 = Spin('s1'), Spin('s2')
>>> exp = 2*s1*s2 + 3*s1
>>> pprint(exp.compile().to_qubo()) # doctest: +SKIP
({('s1', 's1'): 2.0, ('s1', 's2'): 8.0, ('s2', 's2'): -4.0}, -1.0)

Array of Variables
------------------

The :class:`Array` class represents a multi-dimensional array of :class:`Binary` or :class:`Spin` variables.

**Example:** 
Each element of an :class:`Array` can be accessed using indices.

>>> from pyqubo import Array
>>> x = Array.create('x', shape=(2, 3), vartype='BINARY')
>>> x[0, 1] + x[1, 2]
(Binary(x[0][1])+Binary(x[1][2]))


**Example:**
An :class:`Array` can represent the spins in the partitioning problem described above.

>>> from pyqubo import Array
>>> numbers = [4, 2, 7, 1]
>>> s = Array.create('s', shape=4, vartype='SPIN')
>>> H = sum(n * s for s, n in zip(s, numbers))**2
>>> model = H.compile()
>>> qubo, offset = model.to_qubo()
>>> pprint(qubo) # doctest: +SKIP
{('s[0]', 's[0]'): -160.0,
 ('s[0]', 's[1]'): 64.0,
 ('s[0]', 's[2]'): 224.0,
 ('s[0]', 's[3]'): 32.0,
 ('s[1]', 's[1]'): -96.0,
 ('s[1]', 's[2]'): 112.0,
 ('s[1]', 's[3]'): 16.0,
 ('s[2]', 's[2]'): -196.0,
 ('s[2]', 's[3]'): 56.0,
 ('s[3]', 's[3]'): -52.0}


Placeholder
-----------

The :class:`Placeholder` class allows users to quickly update coefficients and parameters, such as the strength of the constraint in a given hamiltonian. 

If the parameter is defined by :class:`Placeholder`, you can specify its value after compilation. In other words, you don't have to re-compile your hamiltonian each time you change parameter values. As it takes longer to compile when the problem size is bigger, the :class:`Placeholder` saves valuable time.

**Example:**
Given the objective function :math:`2a+b` and the constraint :math:`a+b=1` whose hamiltonian is :math:`(a+b-1)^2`, where :math:`a,b` is q-bit variable, the appropriate penalty strength :math:`M` must be used so that the constraint is satisfied. To find the correct :math:`M`, we create a QUBO with different :math:`M` values. In this example, we create a QUBO with :math:`M=5.0` and :math:`M=6.0`.

In the first snippet, we don't use a placeholder. In this case, we need to compile the hamiltonian twice to get a QUBO with :math:`M=5.0` and :math:`M=6.0`.

>>> from pyqubo import Binary
>>> a, b = Binary('a'), Binary('b')
>>> M = 5.0
>>> H = 2*a + b + M*(a+b-1)**2
>>> model = H.compile()
>>> qubo, offset = model.to_qubo() # QUBO with M=5.0
>>> M = 6.0
>>> H = 2*a + b + M*(a+b-1)**2
>>> model = H.compile()
>>> qubo, offset = model.to_qubo() # QUBO with M=6.0

If we define :math:`M` using :class:`Placeholder`, we only have to compile once.

>>> from pyqubo import Placeholder
>>> a, b = Binary('a'), Binary('b')
>>> M = Placeholder('M')
>>> H = 2*a + b + M*(a+b-1)**2
>>> model = H.compile()
>>> qubo, offset = model.to_qubo(feed_dict={'M': 5.0})
>>> qubo, offset = model.to_qubo(feed_dict={'M': 6.0})

The value of the placeholder :math:`M` is specified when calling :obj:`Model.to_qubo()` using a feed_dict.

Decode Solution
---------------

Given a solution from an Ising solver, :obj:`Model.decode_solution()` decodes the solution and returns it in dictionary form.

**Example:** The partitioning problem.

>>> from pyqubo import Array
>>> numbers = [4, 2, 7, 1]
>>> s = Array.create('s', 4, 'SPIN')
>>> H = sum(n * s_i for s_i, n in zip(s, numbers))**2
>>> model = H.compile()
>>> qubo, offset = model.to_qubo()

Let's assume that we get the solution :obj:`{'s[0]': 0, 's[1]': 0, 's[2]': 1, 's[3]': 0}` from the solver.

>>> raw_solution = {'s[0]': 0, 's[1]': 0, 's[2]': 1, 's[3]': 0} # solution from the solver
>>> decoded_solution, broken, energy = model.decode_solution(raw_solution, vartype='BINARY')
>>> pprint(decoded_solution)
{'s': {0: 0, 1: 0, 2: 1, 3: 0}}
>>> broken
{}
>>> energy
0.0

We see that :obj:`decoded_solution` contains the decoded solution of spin vector where the :math:`i` -th element of the vector is accessed via :math:`s[i]`. :obj:`broken` represents broken constraints, which will be explained in the following section. :obj:`energy` represents the energy of the problem.


Validation of Constraints
-------------------------

The :class:`Constraint` wrapper can be used to make the compiler recognize the constraint terms of a hamiltonian. Then, given a solution, :obj:`Model.decode_solution()` can also show whether any constraints were broken. In other words, no additional programs have to be written for the validation of constraints.

**Example:** Given the objective function :math:`2a+b`, and the constraint :math:`a+b=1` whose hamiltonian is :math:`(a+b-1)^2`, where :math:`a,b` is a q-bit variable, we can wrap :math:`(a+b-1)^2` using :class:`Constraint` to signal to the compiler that this part of the hamiltonian is a constraint, i.e., it should be zero when the solution is not broken.

>>> from pyqubo import Binary, Constraint
>>> a, b = Binary('a'), Binary('b')
>>> M = 5.0 # strength of the constraint
>>> H = 2*a + b + M * Constraint((a+b-1)**2, label='a+b=1')
>>> model = H.compile()

Let's assume that we get the solution :obj:`{'a': 1, 'b': 1}` from the solver, which breaks the constraint :math:`a+b=1`.

>>> raw_solution = {'a': 1, 'b': 1}
>>> decoded_solution, broken, energy = model.decode_solution(raw_solution, vartype='BINARY')
>>> pprint(broken)
{'a+b=1': {'penalty': 1.0, 'result': {'a': 1, 'b': 1}}}

:obj:`broken` object contains information about the broken constraint. If no constraint is broken, :obj:`broken` is empty.
