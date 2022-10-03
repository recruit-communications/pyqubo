.. currentmodule:: pyqubo

Model
=====

Model
-----

.. py:class:: Model

    Model represents binary quadratic optimization problem.
    
    By compiling :class:`Express` object, you get a :class:`Model` object.
    It contains the information about QUBO (or equivalent Ising Model),
    and it also has the function to decode the solution
    into the original variable structure.
    
    .. note::
        We do not need to create this object directly. Instead,
        we get this by compiling `Express` objects.
    
    .. py:attribute:: variables
        :type: list[str]

        The list of labels. The order is corresponds to the index of QUBO or Ising model.

        **Example:**

        When you set `index_label=True` in :func:`to_qubo()` method,
        the resulting QUBO has integer index.
        This property `variables` indicates the mapping of indices and labels.

        >>> from pyqubo import Binary
        >>> H = Binary("a") + 2*Binary("b") + 3*Binary("c")
        >>> model = H.compile()
        >>> pprint(model.to_qubo())
        ({('a', 'a'): 1.0, ('b', 'b'): 2.0, ('c', 'c'): 3.0}, 0.0)
        >>> model.to_qubo(index_label=True)  # doctest: +SKIP
        ({(2, 2): 3.0, (1, 1): 2.0, (0, 0): 1.0}, 0.0)
        >>> model.variables
        ['c', 'a', 'b']
        
        This indicaretes the mapping of indices and labels as 'c'->0, 'a'->1, 'b'->2

    **Generate QUBO, Ising model, and BQM**

    .. csv-table::
        :widths: 30, 70

        :func:`to_qubo`, Returns QUBO and energy offset.
        :func:`to_ising`, Returns Ising Model and energy offset.
        :func:`to_bqm`, Returns :class:`dimod.BinaryQuadraticModel`.

    **Interpret samples returned from solvers**

    .. csv-table::
        :widths: 30, 70
        
        :func:`energy`, Returns energy of the sample.
        :func:`decode_sample`, Returns Ising Model and energy offset.
        :func:`decode_sampleset`, Decode the sample represented by :class:`dimod.SampleSet`.


.. py:method:: to_qubo(index_label=False, feed_dict=None)

    Returns QUBO and energy offset.

    :param bool index_label: If true, the keys of returned QUBO are indexed with a positive integer number.
    
    :param dict[str,float] feed_dict: If the expression contains :class:`Placeholder` objects, you have to specify the value of them by :obj:`Placeholder`. Please refer to :class:`Placeholder` for more details.
    
    :return: Tuple of QUBO and energy offset.
        QUBO takes the form of ``dict[(str, str), float]``.
    :rtype: ``tuple[QUBO, float]``
    
    **Examples:**

        This example creates the :obj:`model` from the expression, and
        we get the resulting QUBO by calling :func:`model.to_qubo()`.
        
        >>> from pyqubo import Binary
        >>> x, y, z = Binary("x"), Binary("y"), Binary("z")
        >>> model = (x*y + y*z + 3*z).compile()
        >>> pprint(model.to_qubo()) # doctest: +SKIP
        ({('x', 'x'): 0.0,
        ('x', 'y'): 1.0,
        ('y', 'y'): 0.0,
        ('z', 'y'): 1.0,
        ('z', 'z'): 3.0},
        0.0)
        
        If you want a QUBO which has index labels, specify the argument ``index_label=True``.
        The mapping of the indices and the corresponding labels is
        stored in :obj:`model.variables`.
        
        >>> pprint(model.to_qubo(index_label=True)) # doctest: +SKIP
        ({(0, 0): 3.0, (0, 2): 1.0, (1, 1): 0.0, (1, 2): 1.0, (2, 2): 0.0}, 0.0)
        >>> model.variables
        ['z', 'x', 'y']


.. py:method:: to_ising(index_label=False, feed_dict=None)

    Returns Ising Model and energy offset.

    :param bool index_label: If true, the keys of returned QUBO are indexed with a positive integer number.
    
    :param dict[str,float] feed_dict: If the expression contains :class:`Placeholder` objects, you have to specify the value of them by :obj:`Placeholder`. Please refer to :class:`Placeholder` for more details.
    
    :return: Tuple of Ising Model and energy offset. Where `linear` takes the form of ``(dict[str, float])``, and `quadratic` takes the form of ``dict[(str, str), float]``.
    :rtype: ``tuple(linear, quadratic, float)``
    
    **Examples:**

        This example creates the :obj:`model` from the expression, and
        we get the resulting Ising model by calling :func:`to_ising()`.
        
        >>> from pyqubo import Binary
        >>> x, y, z = Binary("x"), Binary("y"), Binary("z")
        >>> model = (x*y + y*z + 3*z).compile()
        >>> pprint(model.to_ising()) # doctest: +SKIP
        ({'x': 0.25, 'y': 0.5, 'z': 1.75}, {('x', 'y'): 0.25, ('z', 'y'): 0.25}, 2.0)
        
        If you want a Ising model which has index labels,
        specify the argument ``index_label=True``.
        The mapping of the indices and the corresponding labels is
        stored in :obj:`model.variables`.
        
        >>> pprint(model.to_ising(index_label=True)) # doctest: +SKIP
        ({0: 1.75, 1: 0.25, 2: 0.5}, {(0, 2): 0.25, (1, 2): 0.25}, 2.0)
        >>> model.variables
        ['z', 'x', 'y']


.. py:method:: to_bqm(index_label=False, feed_dict=None)
    
    Returns :class:`dimod.BinaryQuadraticModel`.
        
    For more details about :class:`dimod.BinaryQuadraticModel`,
    see `dimod.BinaryQuadraticModel 
    <https://docs.ocean.dwavesys.com/projects/dimod/en/latest/reference/bqm/index.html>`_.
    
    :param bool index_label: If true, the keys of returned QUBO are indexed with a positive integer number.
    :param dict[str,float] feed_dict: If the expression contains :class:`Placeholder` objects, you have to specify the value of them by :obj:`Placeholder`.
    
    :return: :class:`dimod.BinaryQuadraticModel` with vartype set to `dimod.BINARY`.
    :rtype: :class:`dimod.BinaryQuadraticModel`

    **Examples:**

    >>> from pyqubo import Binary, Constraint
    >>> from dimod import ExactSolver
    >>> a, b = Binary('a'), Binary('b')
    >>> H = Constraint(2*a-3*b, "const1") + Constraint(a+b-1, "const2")
    >>> model = H.compile()
    >>> bqm = model.to_bqm()
    >>> sampleset = ExactSolver().sample(bqm)
    >>> decoded_samples = model.decode_sampleset(sampleset)
    >>> best_sample = min(decoded_samples, key=lambda s: s.energy)
    >>> print(best_sample.energy)
    -3.0
    >>> pprint(best_sample.sample)
    {'a': 0, 'b': 1}
    >>> pprint(best_sample.constraints())
    {'const1': (False, -3.0), 'const2': (True, 0.0)}


.. py:method:: energy(solution, vartype, feed_dict=None)

    Returns energy of the sample.
        
    :param list[int]/dict[str,int] sample: The sample returned from solvers.
    :param str vartype: Variable type of the solution. Specify either ``'BINARY'`` or ``'SPIN'``. 
    :param dict[str,float] feed_dict: Specify the placeholder values.
        
    :return: Calculated energy.
    :rtype: float


.. py:method:: decode_sample(sample, vartype, feed_dict=None)

    Decode sample from solvers.
    
    :param list[int]/dict[str,int] sample: The sample returned from solvers.
    :param str vartype: Variable type of the solution. Specify either ``'BINARY'`` or ``'SPIN'``. 
    :param dict[str,float] feed_dict: Specify the placeholder values.
        
    :return: :class:`DecodedSample` object.
    :rtype: :class:`DecodedSample`

    **Examples**

    >>> from pyqubo import Binary, SubH
    >>> a, b = Binary('a'), Binary('b')
    >>> H = SubH(a+b-2, "subh1") + 2*a + b
    >>> model = H.compile()
    >>> decoded_sample = model.decode_sample({'a': 1, 'b': 0}, vartype='BINARY')
    >>> print(decoded_sample.energy)
    1.0
    >>> pprint(decoded_sample.sample)
    {'a': 1, 'b': 0}
    >>> print(decoded_sample.subh)
    {'subh1': -1.0}


.. py:method:: decode_sampleset(sampleset, feed_dict=None)

    Decode the sample represented by :class:`dimod.SampleSet`.
        
    For more details about :class:`dimod.SampleSet`,
    see `dimod.SampleSet 
    <https://docs.ocean.dwavesys.com/projects/dimod/en/latest/reference/sampleset.html#id1>`_.
        
    :param `dimod.SampleSet` sample: The solution returned from dimod sampler.
    :param dict[str,float] feed_dict: Specify the placeholder values. Default=None
    
    :return: :class:`DecodedSample` object.
    :rtype: :class:`DecodedSample`

    **Examples**

    >>> from pyqubo import Binary, Constraint
    >>> from dimod import ExactSolver
    >>> a, b = Binary('a'), Binary('b')
    >>> H = Constraint(2*a-3*b, "const1") + Constraint(a+b-1, "const2")
    >>> model = H.compile()
    >>> bqm = model.to_bqm()
    >>> sampleset = ExactSolver().sample(bqm)
    >>> decoded_samples = model.decode_sampleset(sampleset)
    >>> best_sample = min(decoded_samples, key=lambda s: s.energy)
    >>> print(best_sample.energy)
    -3.0
    >>> pprint(best_sample.sample)
    {'a': 0, 'b': 1}
    >>> pprint(best_sample.constraints())
    {'const1': (False, -3.0), 'const2': (True, 0.0)}


DecodedSample
-------------

.. py:class:: DecodedSample

    DecodedSample contains the informatin like whether the constraint is satisfied or not, or the value of the SubHamiltonian.

    .. py:attribute:: sample
        :type: dict[str,int]

        The value of variables specified by label.
        The dictionary with the key being the label and the value being the corresponding value.

    .. py:attribute:: energy
        :type: float

        The energy of the entire Hamiltonian.

    .. py:attribute:: subh
        :type: dict[str, int]

        The value of the sub-Hamiltonian with the key being the `label` of `SubH` object.

    **Examples**

    >>> from pyqubo import Binary, SubH
    >>> a, b = Binary('a'), Binary('b')
    >>> H = SubH(a+b-2, "subh1") + 2*a + b
    >>> model = H.compile()
    >>> decoded_sample = model.decode_sample({'a': 1, 'b': 0}, vartype='BINARY')
    >>> print(decoded_sample.energy)
    1.0
    >>> pprint(decoded_sample.sample)
    {'a': 1, 'b': 0}
    >>> print(decoded_sample.subh)
    {'subh1': -1.0}

    **Methods**

    .. csv-table::
        :widths: 30, 70
        
        :func:`array`, Get the value of the array element specified.
        :func:`constraints`, Returns the information about constraints.


.. py:method:: array(array_name, index)

    Get the value of the array specified by `array_name` and `index`.

    :param str array_name: The name of the array.
    :param int/tuple index: The index of the array.

    :return: The value of the array calculated by the sample.
    :rtype: float

    **Examples**

    >>> from pyqubo import Array
    >>> x = Array.create('x', shape=(2, 1), vartype="BINARY")
    >>> H = (x[0, 0] + x[1, 0] - 1)**2
    >>> model = H.compile()
    >>> qubo, offset = model.to_qubo()
    >>> pprint(qubo)
    {('x[0][0]', 'x[0][0]'): -1.0,
    ('x[0][0]', 'x[1][0]'): 2.0,
    ('x[1][0]', 'x[1][0]'): -1.0}
    >>> dec = model.decode_sample({'x[0][0]': 1, 'x[1][0]': 0}, vartype='BINARY')
    >>> print(dec.array('x', (0, 0)))
    1
    >>> print(dec.array('x', (1, 0)))
    0


.. py:method:: constraints(only_broken)

    Get the value of the array specified by `array_name` and `index`.

    :param bool only_broken: Whether to select only broken constraints.

    :return: Dictionary with the key being the label of the constraint and the value being
        the boolean and the corresponding energy value. The boolean value indicates whether the constraint is satisfied or not.
    
    :rtype: dict[str, tuple[bool, float]]

    **Examples**

    >>> from pyqubo import Binary, Constraint
    >>> a, b = Binary('a'), Binary('b')
    >>> H = Constraint(a+b-2, "const1") + Constraint(a+b-1, "const2")
    >>> model = H.compile()
    >>> dec = model.decode_sample({'a': 1, 'b': 0}, vartype='BINARY')
    >>> pprint(dec.constraints())
    {'const1': (False, -1.0), 'const2': (True, 0.0)}
    >>> pprint(dec.constraints(only_broken=True))
    {'const1': (False, -1.0)}
