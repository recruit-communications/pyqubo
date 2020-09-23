Model
=======

.. py:class:: Model

    Model represents binary quadratic optimization problem.
    
    By compiling :class:`Express` object, you get a :class:`Model` object.
    It contains the information about QUBO (or equivalent Ising Model),
    and it also has the function to decode the solution
    into the original variable structure.
    
    .. note::
        We do not need to create this object directly. Instead,
        we get this by compiling `Express` objects.
    
    
    .. py:attribute:: variable_order

        list variable_order The list of labels. The order is corresponds to the index of QUBO or Ising model.
        
    :param dict[int, label] index2label: The dictionary which maps an index to a label.
        
        label2index (dict[label, index]):
            The dictionary which maps a label to an index.