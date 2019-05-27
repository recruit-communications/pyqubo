import unittest

from pyqubo import VarSet, VarSetFromSubH, VarSetFromVarLabels
from pyqubo import OrVars, AndVars
from pyqubo import Binary
from pyqubo import SubH


class TestVarSet(unittest.TestCase):

    def test_and_from_model(self):
        a, b, c = Binary("a"), Binary("b"), Binary("c")
        exp = (SubH(a + b, 'n1') + SubH(b + c, 'n2'))**2
        model = exp.compile()

        set_x = VarSetFromSubH(model, 'n1')
        set_y = VarSetFromSubH(model, 'n2')
        set_z = AndVars(set_x, set_y)

        self.assertTrue(set_x.var_names() == {'a', 'b'})
        self.assertTrue(set_y.var_names() == {'b', 'c'})
        self.assertTrue(set_z.var_names() == {'b'})

    def test_and_from_vars(self):
        a, b, c = Binary("a"), Binary("b"), Binary("c")

        set_x = VarSetFromVarLabels([a, b])
        set_y = VarSetFromVarLabels([b, c])
        set_z = AndVars(set_x, set_y)

        self.assertTrue(set_x.var_names() == {'a', 'b'})
        self.assertTrue(set_y.var_names() == {'b', 'c'})
        self.assertTrue(set_z.var_names() == {'b'})

    def test_or_from_model(self):
        a, b, c = Binary("a"), Binary("b"), Binary("c")
        exp = (SubH(a + b, 'n1') + SubH(b + c, 'n2'))**2
        model = exp.compile()

        set_x = VarSetFromSubH(model, 'n1')
        set_y = VarSetFromSubH(model, 'n2')
        set_z = OrVars(set_x, set_y)

        self.assertTrue(set_x.var_names() == {'a', 'b'})
        self.assertTrue(set_y.var_names() == {'b', 'c'})
        self.assertTrue(set_z.var_names() == {'a', 'b', 'c'})

    def test_or_from_vars(self):
        a, b, c = Binary("a"), Binary("b"), Binary("c")

        set_x = VarSetFromVarLabels([a, b])
        set_y = VarSetFromVarLabels([b, c])
        set_z = OrVars(set_x, set_y)

        self.assertTrue(set_x.var_names() == {'a', 'b'})
        self.assertTrue(set_y.var_names() == {'b', 'c'})
        self.assertTrue(set_z.var_names() == {'a', 'b', 'c'})


