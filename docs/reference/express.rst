.. currentmodule:: pyqubo

Expression
==========

.. py:class:: Base

    Abstract class of pyqubo expression.
    
    All basic component class such as :class:`.Binary`, :class:`.Spin` or :class:`.Add`
    inherits :class:`.Base`.
    
    For example, an expression :math:`2ab+1` (where :math:`a, b` is :class:`Binary` variable) is
    represented by the binary tree above.
    
    .. note::
        This class is an abstract class of all component of expressions.
    
    **Example:**

        We write mathematical expressions with objects such as :class:`Binary` or :class:`Spin`
        which inherit :class:`.Base`.
        
        >>> from pyqubo import Binary
        >>> a, b = Binary("a"), Binary("b")
        >>> 2*a*b + 1
        (((2.000000 * Binary('a')) * Binary('b')) + 1.000000)


.. py:method:: compile(strength=5.0)

        Returns the compiled :class:`Model`.
        
        This method reduces the degree of the expression if the degree is higher than 2,
        and convert it into :class:`.Model` which has information about QUBO.
        
        :param float strength: The strength of the reduction constraint.
                Insufficient strength can result in the binary quadratic model
                not having the same minimizations as the polynomial.
        :return: The model compiled from the :class:`.Base`.
        :rtype: :class:`Model`

        **Examples:**

            In this example, there are higher order terms :math:`abc` and :math:`abd`. It is decomposed as
            [[``a*b``, ``c``], ``d``] hierarchically and converted into QUBO.
            By calling :func:`to_qubo()` of the :obj:`model`, we get the QUBO.
            
            >>> from pyqubo import Binary
            >>> a, b, c, d = Binary("a"), Binary("b"), Binary("c"), Binary("d")
            >>> model = (a*b*c + a*b*d).compile()
            >>> pprint(model.to_qubo()) # doctest: +SKIP
            ({('a', 'a'): 0.0,
              ('a', 'a*b'): -10.0,
              ('a', 'b'): 5.0,
              ('a*b', 'a*b'): 15.0,
              ('a*b', 'b'): -10.0,
              ('a*b', 'c'): 1.0,
              ('a*b', 'd'): 1.0,
              ('b', 'b'): 0.0,
              ('c', 'c'): 0,
              ('d', 'd'): 0},
             0.0)

Binary
------

.. py:class:: Binary(label)

    Binary variable i.e. {0, 1}.
    
    :param str label: The label of a variable. A variable is identified by this label.
        
    **Example:**

        Example code to create an expression.

        >>> from pyqubo import Binary
        >>> a, b = Binary('a'), Binary('b')
        >>> exp = 2*a*b + 3*a
        >>> pprint(exp.compile().to_qubo())   # doctest: +SKIP
        ({('a', 'a'): 3.0, ('a', 'b'): 2.0, ('b', 'b'): 0}, 0.0)

Spin
----

.. py:class:: Spin(label)

    Spin variable i.e. {-1, 1}.
    
    :param str label: The label of a variable. A variable is identified by this label.

    **Example:**

        Example code to create an expression.

        >>> from pyqubo import Spin
        >>> a, b = Spin('a'), Spin('b')
        >>> exp = 2*a*b + 3*a
        >>> pprint(exp.compile().to_qubo()) # doctest: +SKIP
        ({('a', 'a'): 2.0, ('a', 'b'): 8.0, ('b', 'b'): -4.0}, -1.0)

Placeholder
-----------

.. py:class:: Placeholder(label)

    Placeholder expression.
    
    You can specify the value of the :class:`Placeholder` when creating the QUBO.
    By using :class:`Placeholder`, you can change the value without compiling again.
    This is useful when you need to update the strength of constraint gradually.
    
    :param str label: The label of the placeholder.
    
    **Example:**

        The value of the placeholder is specified when you call :func:`to_qubo`.
        
        >>> from pyqubo import Binary, Placeholder
        >>> x, y, a = Binary('x'), Binary('y'), Placeholder('a')
        >>> exp = a*x*y + 2.0*x
        >>> pprint(exp.compile().to_qubo(feed_dict={'a': 3.0})) # doctest: +SKIP
        ({('x', 'x'): 2.0, ('x', 'y'): 3.0, ('y', 'y'): 0}, 0.0)
        >>> pprint(exp.compile().to_qubo(feed_dict={'a': 5.0})) # doctest: +SKIP
        ({('x', 'x'): 2.0, ('x', 'y'): 5.0, ('y', 'y'): 0}, 0.0)

SubH
----

.. py:class:: SubH(hamiltonian, label, as_constraint=False)

    SubH expression.
    The parent class of Constraint. You can specify smaller sub-hamiltonians in your expression.
    
    :param `Base` hamiltonian: The expression you want to specify as a sub-hamiltonian.
    
    :param str label: The label of the sub-hamiltonian. Sub-hamiltonians can be identified
        by their labels.
    
    :param boolean as_constraint: Whether or not the sub-hamiltonian should also be treated
        as a constraint. False by default.
    
    **Example:**

        You can call namespaces to identify the labels defined in a model.

        >>> from pyqubo import Spin, SubH
        >>> s1, s2, s3 = Spin('s1'), Spin('s2'), Spin('s3')
        >>> exp = (SubH(s1 + s2, 'n1'))**2 + (SubH(s1 + s3, 'n2'))**2
        >>> model = exp.compile()
        >>> model.namespaces  #doctest: +SKIP
        ({'n1': {'s1', 's2'}, 'n2': {'s1', 's3'}}, {'s1', 's2', 's3'})

Constraint
----------

.. py:class:: Constraint(hamiltonian, label, condition=lambda x: x==0.0)

    Constraint expression.
    You can specify the constraint part in your expression.
    
    :param `Express` child: The expression you want to specify as a constraint.
    :param str label: The label of the constraint. You can identify constraints by the label.
    :param `func (float => boolean)` condition: function to indicate whether the constraint is satisfied or not.
        Default is `lambda x: x == 0.0`. function takes float value and returns boolean value. 
        You can define the condition where the constraint is satisfied.

    **Example:**

        When the Hamiltonian contains :class:`Constraint`,
        you know whether each constraint is satisfied or not
        by accessing to :class:`DecodedSample`.

        >>> from pyqubo import Binary, Constraint
        >>> a, b = Binary('a'), Binary('b')
        >>> H = Constraint(a+b-2, "const1") + Constraint(a+b-1, "const2")
        >>> model = H.compile()
        >>> dec = model.decode_sample({'a': 1, 'b': 0}, vartype='BINARY')
        >>> pprint(dec.constraints())
        {'const1': (False, -1.0), 'const2': (True, 0.0)}
        >>> pprint(dec.constraints(only_broken=True))
        {'const1': (False, -1.0)}

Num
---
    
.. py:class:: Num(value)

    Expression of number
    
    :param float value: the value of the number.
    
    **Example:**

        Example code to create an expression.

        >>> from pyqubo import Binary, Num
        >>> a = Binary('a')
        >>> a + 1
        (Binary('a') + 1.000000)
        >>> a + Num(1)
        (Binary('a') + 1.000000)

UserDefinedExpress
------------------

.. py:class:: UserDefinedExpress()

    User defined express.
    
    User can define their own expression by inheriting :class:`UserDefinedExpress`.
    
    **Example:**

        Define the :class:`LogicalAnd` class by inheriting :class:`UserDefinedExpress`.
        
        >>> from pyqubo import UserDefinedExpress, Binary
        >>> class LogicalAnd(UserDefinedExpress):
        ...     def __init__(self, bit_a, bit_b):
        ...         express = bit_a * bit_b
        ...         super().__init__(express)
        >>> a, b = Binary('a'), Binary('b')
        >>> logical_and = LogicalAnd(a, b)

WithPenalty
-----------

.. py:class:: WithPenalty()

    You can define the custum penalty class by inheriting `WithPenalty`.
    The `penalty` argument will be added to the generated Hamiltonian.
    Integer classes with constraints, such as :class:`OneHotEncInteger`, are defined using this class.

    **Example:**

    Define the custom penalty class inheriting `WithPenalty`.
    We initialize this class with `hamiltonian` :math:`h`.
    The constraint term :math:`(h-1)^2` will be added to the generated Hamiltonian.
    
    >>> from pyqubo import WithPenalty
    >>> class CustomPenalty(WithPenalty):
    ...     def __init__(self, hamiltonian, label, strength):
    ...         penalty = strength * (hamiltonian-1)**2
    ...         super().__init__(hamiltonian, penalty, label)
    >>> a, b = Binary("a"), Binary("b")
    >>> p = CustomPenalty(a+b, label="penalty", strength=2.0)
    >>> model = (p+1).compile()
    >>> qubo, offset = model.to_qubo()
