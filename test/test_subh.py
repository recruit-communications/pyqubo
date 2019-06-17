import unittest

from pyqubo import SubH, Spin


class TestSubH(unittest.TestCase):

    def test_namespaces(self):
        s1, s2, s3 = Spin("s1"), Spin("s2"), Spin("s3")
        H = (SubH(2*s1 + 4*s2, "n1") + SubH(6*s3 + s2, "n2"))**2
        model = H.compile()

        self.assertTrue(model.namespaces[0]['n1'] == {'s1', 's2'})
        self.assertTrue(model.namespaces[0]['n2'] == {'s2', 's3'})
