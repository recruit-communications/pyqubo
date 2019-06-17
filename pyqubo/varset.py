import abc
import six


@six.add_metaclass(abc.ABCMeta)
class VarSet:
    @abc.abstractmethod
    def var_names(self, model):
        pass


class VarSetFromSubH(VarSet):
    """Creates a VarSet from SubH instances specified in a model.

    Args:
        label (:class:`VarSet`): VarSet instance

        model (:class:`Model`): Model instance

    """

    def __init__(self, label):
        super(VarSetFromSubH, self).__init__()
        self.label = label

    def var_names(self, model):  # take model here
        return model.namespaces[0][self.label]


class VarSetFromVarLabels(VarSet):
    """Creates a VarSet from a provided list of variables.

    Args:
        var_list: a list of variables

        model (:class:`Model`): Model instance

    """

    def __init__(self, var_list):
        super(VarSetFromVarLabels, self).__init__()
        self.var_list = var_list

    def var_names(self, model):
        return set(
            var.label for var in self.var_list
        )


class AndVars(VarSet):
    """Creates a VarSet that contains the intersection of two VarSet instances.

    Args:
        set_a (:class:`VarSet`): VarSet instance

        set_b (:class:`VarSet`): VarSet instance

        model (:class:`Model`): Model instance

    Examples:
        In this example, two VarSet instances are created from the SubH class. AndVars
        provides the common variable namespaces between these two sets.

        >>> a, b, c = Binary("a"), Binary("b"), Binary("c")
        >>> exp = (SubH(a + b, 'n1') + SubH(b + c, 'n2'))**2
        >>> model = exp.compile()
        >>> set_x = VarSetFromSubH('n1')
        >>> set_y = VarSetFromSubH('n2')
        >>> set_z = AndVars(set_x, set_y)
        >>> set_z.var_names(model)
        {'b'}
    """

    def __init__(self, set_a, set_b):
        super(AndVars, self).__init__()
        self.set_a = set_a
        self.set_b = set_b

    def var_names(self, model):
        return self.set_a.var_names(model) & self.set_b.var_names(model)


class OrVars(VarSet):
    """Creates a VarSet that contains the union of two VarSet instances.

    Args:
        set_a (:class:`VarSet`): VarSet instance

        set_b (:class:`VarSet`): VarSet instance

        model (:class:`Model`): Model instance

    Examples:
        In this example, two VarSet instances are created from the SubH class. OrVars
        provides all namespaces contained in these two sets.

        >>> a, b, c = Binary("a"), Binary("b"), Binary("c")
        >>> exp = (SubH(a + b, 'n1') + SubH(b + c, 'n2'))**2
        >>> model = exp.compile()
        >>> set_x = VarSetFromSubH('n1')
        >>> set_y = VarSetFromSubH('n2')
        >>> set_z = OrVars(set_x, set_y)
        >>> set_z.var_names(model)
        {'a','b','c'}
    """

    def __init__(self, set_a, set_b):
        super(OrVars, self).__init__()
        self.set_a = set_a
        self.set_b = set_b

    def var_names(self, model):
        return self.set_a.var_names(model) | self.set_b.var_names(model)
