import abc
import six
from .core import Model


@six.add_metaclass(abc.ABCMeta)
class VarSet:
    @abc.abstractmethod
    def var_names(self):
        pass


class AndVars(VarSet):
    def __init__(self, set_a, set_b):
        super(AndVars, self).__init__()
        self.set_a = set_a
        self.set_b = set_b

    def var_names(self):
        return self.set_a.var_names() & self.set_b.var_names()


class OrVars(VarSet):
    def __init__(self, set_a, set_b):
        super(OrVars, self).__init__()
        self.set_a = set_a
        self.set_b = set_b

    def var_names(self):
        return self.set_a.var_names() | self.set_b.var_names()


class VarSetFromSubH(VarSet):
    def __init__(self, model, label):
        super(VarSetFromSubH, self).__init__()
        self.model = model
        self.label = label

    def var_names(self):
        assert isinstance(self.model, Model)
        return self.model.namespaces[0][self.label]


class VarSetFromVarLabels(VarSet):
    def __init__(self, var_list):
        super(VarSetFromVarLabels, self).__init__()
        self.var_list = var_list

    def var_names(self):
        return set(
            var.label for var in self.var_list
        )
