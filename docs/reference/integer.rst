:orphan:

.. currentmodule:: pyqubo

Integer
=======

Summary of each integer encoding, whose value takes [0, n].

.. csv-table::
   :header: Encoding, Value, Constraint, #vars, Max abs. coeff of value
   :widths: 5, 4, 5, 5, 5

   :class:`UnaryEncInteger`, :math:`\sum_{i=1}^{n}x_{i}`, No constraint, :math:`n`, :math:`1`
   :class:`LogEncInteger`, :math:`\sum_{i=1}^{d}2^i x_{i}`, No constraint, :math:`\lceil\log_{2}n\rceil(=d)`, :math:`2^d`
   :class:`OneHotEncInteger`, :math:`\sum_{i=0}^{n}ix_{i}`, :math:`(\sum_{i=0}^{n}x_{i}-1)^2`, :math:`n+1`, :math:`n`
   :class:`OrderEncInteger`, :math:`\sum_{i=1}^{n}x_{i}`, :math:`\sum_{i=1}^{n-1}x_{i+1}(1-x_{i})`, :math:`n`, :math:`1`


UnaryEncInteger
---------------

.. autoclass:: UnaryEncInteger
    :members:

LogEncInteger
-------------

.. autoclass:: LogEncInteger
    :members:

OneHotEncInteger
----------------

.. autoclass:: OneHotEncInteger
    :members:


OrderEncInteger
---------------

.. autoclass:: OrderEncInteger
    :members:


.. rubric:: References

.. [TaTK09] Tamura, N., Taga, A., Kitagawa, S., & Banbara, M. (2009). Compiling finite linear CSP into SAT. Constraints, 14(2), 254-272.
