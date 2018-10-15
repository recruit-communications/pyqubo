.. automodule:: pyqubo

Getting Started
===============

Installation
------------

If you use pip, just type

.. code-block:: shell

    pip install pyqubo

You can install from the source code like

.. code-block:: shell

    git clone https://github.com/recruit-communications/pyqubo.git
    cd pyqubo
    python setup.py install


QUBO and Ising Model
--------------------

If you want to solve a combinatorial optimization problem by quantum or classical annealing machines, you need to represent your problem in QUBO (Quadratic Unconstrained Binary Optimization) or Ising model. PyQUBO converts your problem into QUBO or Ising model format.

The objective function of **QUBO** is defined as:

.. math::

    \sum_{ij}q_{ij}x_{i}x_{j}


where :math:`x_{i}` represents a binary variable which takes 0 or 1, and :math:`q_{ij}` represents a quadratic coefficient.

The objective function of **Ising model** is defined as:

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
>>> pprint(qubo)
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

In this example, you want to solve `Number Partitioning Problem <https://en.wikipedia.org/wiki/Partition_problem>`_ with a set S = {4, 2, 7, 1}. The hamiltonian :math:`H` is represented as

.. math::

    H = (4 s_{1} + 2 s_{2} + 7 s_{3} + s_{4})^2

where :math:`s_{i}` is a :math:`i` th spin variable which indicates a group the :math:`i` th number should belong to.
In PyQUBO, spin variables are internally converted to binary variables via the relationship :math:`x_{i} = (s_{i}+1)/2`. The QUBO coefficents and the offset returned from :obj:`Model.to_qubo()` represents the following objective function:

.. math::

    &-160 x_{1}x_{1} + 64 x_{1}x_{2} + 224 x_{1}x_{3} + 32 x_{1}x_{4} - 96 x_{2}x_{2}\\
    &+ 112 x_{2}x_{3} + 16 x_{2}x_{4} - 196 x_{3}x_{3} + 56 x_{3}x_{4} - 52 x_{4}x_{4} + 196


4. **Call ‘to_ising()’ to get Ising coefficients.**

If you want to get the coefficient of the Ising model, just call :obj:`Model.to_ising()` method like below.

>>> linear, quadratic, offset = model.to_ising()
>>> pprint(linear)
{'s1': 0.0, 's2': 0.0, 's3': 0.0, 's4': 0.0}
>>> pprint(quadratic)
{('s1', 's2'): 16.0,
 ('s1', 's3'): 56.0,
 ('s1', 's4'): 8.0,
 ('s2', 's3'): 28.0,
 ('s2', 's4'): 4.0,
 ('s3', 's4'): 14.0}
>>> print(offset)
70.0

where `linear` represents external magnetic fields :math:`h`, `quadratic` represents interactions :math:`J` and `offset` represents the constant value in the objective function below.

.. math::

    16 s_{1}s_{2} + 56 s_{1}s_{3} + 8 s_{1}s_{4} + 28 s_{2}s_{3} + 4 s_{2}s_{4} + 14 s_{3}s_{4} + 70


Variable: Qbit and Spin
-----------------------

When you define a hamiltonian, you can use :class:`Qbit` or :class:`Spin` as a variable.

**Example:**
If you want to define a hamiltonian with binary variables :math:`x \in \{0, 1\}`, use :class:`Qbit`.

>>> from pyqubo import Qbit
>>> x1, x2 = Qbit('x1'), Qbit('x2')
>>> exp = 2*x1*x2 + 3*x1
>>> pprint(exp.compile().to_qubo())
({('x1', 'x1'): 3.0, ('x1', 'x2'): 2.0, ('x2', 'x2'): 0.0}, 0.0)

**Example:**
If you want to define a hamiltonian with spin variables :math:`s \in \{-1, 1\}`, use :class:`Spin`.

>>> from pyqubo import Spin
>>> s1, s2 = Spin('s1'), Spin('s2')
>>> exp = 2*s1*s2 + 3*s1
>>> pprint(exp.compile().to_qubo())
({('s1', 's1'): 2.0, ('s1', 's2'): 8.0, ('s2', 's2'): -4.0}, -1.0)

Vector and Matrix
-----------------

:class:`Vector` is a 1-dim array and :class:`Matrix` is a 2-dim array of :class:`Qbit` or :class:`Spin`.

**Example:** You can access each element of the vector with an index like:

>>> from pyqubo import Vector
>>> x = Vector('x', n_dim=3)
>>> x[0] + x[2]
(Qbit(x[0])+Qbit(x[2]))

**Example:** You can access each element of the matrix with an index like:

>>> from pyqubo import Matrix
>>> x = Matrix('x', n_row=2, n_col=3)
>>> x[0, 1] + x[1, 2]
(Qbit(x[0][1])+Qbit(x[1][2]))


**Example:**
You can use :class:`Vector` to represent multiple spins in the example of partitioning problem above.

>>> from pyqubo import Vector
>>> numbers = [4, 2, 7, 1]
>>> s = Vector('s', n_dim=4, spin=True)
>>> H = sum(n * s for s, n in zip(s, numbers))**2
>>> model = H.compile()
>>> qubo, offset = model.to_qubo()
>>> pprint(qubo)
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

If you have a parameter that you will probably update, such as the strength of the constraints in your hamiltonian, using :class:`Placeholder` will save your time.
If you define the parameter by :class:`Placeholder`, you can specify the value of the parameter after compile.
This means that you don't have to compile repeatedly for getting QUBOs with various parameter values.
It takes longer time to execute a compile when the problem size is bigger. In that case, you can save your time by using :class:`Placeholder`.

**Example:**
If you have an objective function :math:`2a+b`, and a constraint :math:`a+b=1` whose hamiltonian is :math:`(a+b-1)^2` where :math:`a,b` is qbit variable, you need to find the penalty strength :math:`M` such that the constraint is satisfied. Thus, you need to create QUBO with different values of :math:`M`. In this example, we create QUBO with :math:`M=5.0` and :math:`M=6.0`.

In the first code, we don't use placeholder. In this case, you need to compile the hamiltonian twice to get a QUBO with :math:`M=5.0` and :math:`M=6.0`.

>>> from pyqubo import Qbit
>>> a, b = Qbit('a'), Qbit('b')
>>> M = 5.0
>>> H = 2*a + b + M*(a+b-1)**2
>>> model = H.compile()
>>> qubo, offset = model.to_qubo() # QUBO with M=5.0
>>> M = 6.0
>>> H = 2*a + b + M*(a+b-1)**2
>>> model = H.compile()
>>> qubo, offset = model.to_qubo() # QUBO with M=6.0

If you don't want to compile twice, define :math:`M` by :class:`Placeholder`.

>>> from pyqubo import Placeholder
>>> a, b = Qbit('a'), Qbit('b')
>>> M = Placeholder('M')
>>> H = 2*a + b + M*(a+b-1)**2
>>> model = H.compile()
>>> qubo, offset = model.to_qubo(feed_dict={'M': 5.0})

You get a QUBO with different value of M without compile

>>> qubo, offset = model.to_qubo(feed_dict={'M': 6.0})

The actual value of the placeholder :math:`M` is specified in calling :obj:`Model.to_qubo()` as a value of the feed_dict.

Decode Solution
---------------

When you get a solution from the Ising solver, :obj:`Model.decode_solution()` decodes the solution and returns decoded_solution in dictionary form.

**Example:** You are solving a partitioning problem.

>>> from pyqubo import Vector
>>> numbers = [4, 2, 7, 1]
>>> s = Vector('s', 4, spin=True)
>>> H = sum(n * s_i for s_i, n in zip(s, numbers))**2
>>> model = H.compile()
>>> qubo, offset = model.to_qubo()

Let's assume that you get a solution :obj:`{'s[0]': 0, 's[1]': 0, 's[2]': 1, 's[3]': 0}` from the solver.

>>> raw_solution = {'s[0]': 0, 's[1]': 0, 's[2]': 1, 's[3]': 0} # solution from the solver
>>> decoded_solution, broken, energy = model.decode_solution(raw_solution, vartype='BINARY')
>>> pprint(decoded_solution)
{'s': {0: 0, 1: 0, 2: 1, 3: 0}}
>>> broken
{}
>>> energy
0.0

You can see that :obj:`decoded_solution` has the decoded solution of spin vector where :math:`i` th element of the vector is accessed via `s[i]`.
:obj:`broken` represents broken constraint which will be explained in the following section.
:obj:`energy` represents energy of the problem.


Validation of Constraints
-------------------------

When the hamiltonian has constraints, you can let the compiler recognize the hamiltonian of the constraint with :class:`Constraint`.
When you decode the solution, the model let you know which constraints are broken.
You don't have to write additional programs for validation of the constraints.

**Example:** If you have an objective function :math:`2a+b`, and a constraint :math:`a+b=1` whose hamiltonian is :math:`(a+b-1)^2` where :math:`a,b` is qbit variable, you need to put :math:`(a+b-1)^2` in :class:`Constraint` to tell the compiler that this hamiltonian is constraint i.e. it should be zero when the solution is not broken.

>>> from pyqubo import Qbit, Constraint
>>> a, b = Qbit('a'), Qbit('b')
>>> M = 5.0 # strength of the constraint
>>> H = 2*a + b + M * Constraint((a+b-1)**2, label='a+b=1')
>>> model = H.compile()

Let's assume that you get a solution :obj:`{'a': 1, 'b': 1}` from the solver which breaks the constraint :math:`a+b=1`.

>>> raw_solution = {'a': 1, 'b': 1}
>>> decoded_solution, broken, energy = model.decode_solution(raw_solution, vartype='BINARY')
>>> pprint(broken)
{'a+b=1': {'penalty': 1.0, 'result': {'a': 1, 'b': 1}}}

:obj:`broken` object contains the information about the broken constraint.
If no constraint is broken, :obj:`broken` is empty.

