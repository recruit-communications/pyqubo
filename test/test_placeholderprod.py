# Copyright 2018 Recruit Communications Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

from pyqubo import PlaceholderProd


class TestPlaceholderProd(unittest.TestCase):

    def test_equality(self):
        term_key1 = PlaceholderProd({"a": 1, "b": 2})
        term_key2 = PlaceholderProd({"a": 1, "b": 2})
        term_key3 = PlaceholderProd({"a": 2, "b": 1})
        self.assertTrue(term_key1 == term_key2)
        self.assertTrue(term_key1 != term_key3)
        self.assertTrue(term_key1 != 1)

    def test_equality_const(self):
        term_key1 = PlaceholderProd({})
        term_key2 = PlaceholderProd({})
        term_key3 = PlaceholderProd({'a': 1})
        self.assertTrue(term_key1.is_constant())
        self.assertEqual(term_key1, term_key2)
        self.assertNotEqual(term_key1, term_key3)

    def test_merge(self):
        term_key1 = PlaceholderProd({"a": 1, "b": 2})
        term_key2 = PlaceholderProd({"a": 1, "b": 1})
        term_key3 = PlaceholderProd({"a": 2, "b": 3})
        term_key4 = PlaceholderProd({})
        self.assertEqual(term_key3, PlaceholderProd.merge_term_key(term_key1, term_key2))
        self.assertEqual(term_key1, PlaceholderProd.merge_term_key(term_key1, term_key4))

    def test_evaluate(self):
        term_key1 = PlaceholderProd({"a": 1, "b": 2})
        empty_key = PlaceholderProd({})
        dict_value = {"a": 3.0, "b": 5.0}
        prod = term_key1.calc_product(dict_value)
        expected_prod = 75
        self.assertEqual(expected_prod, prod)
        self.assertEqual(1, empty_key.calc_product({}))

    def test_repr(self):
        term_key1 = PlaceholderProd({"a": 2, "b": 3})
        empty_key = PlaceholderProd({})
        self.assertIn(repr(term_key1), "a^2*b^3")
        self.assertEqual(repr(empty_key), "const")
