import unittest
from jenkinsapi.label_expression import Token, LabelExpression

class TestLabelExpression(unittest.TestCase):

    def test_labelexpr_single_label(self):
        le = LabelExpression('label')
        self.assertEqual(le.tokens[0], Token('ID', 'label'))
        self.assertTrue(le.matches(['label']))
        self.assertFalse(le.matches(['foo']))

    def test_labelexpr_group(self):
        le = LabelExpression('(this||that)&&other')
        self.assertEqual(le.tokens, [Token('GROUP', [Token('ID', 'this'), Token('OR', '||'), Token('ID', 'that')]),
                                           Token('AND', "&&"), Token('ID', 'other')])
        self.assertTrue(le.matches(['this', 'other']))
        self.assertTrue(le.matches(['that', 'other']))
        self.assertFalse(le.matches(['other']))
        self.assertFalse(le.matches(['this']))
        self.assertFalse(le.matches(['that']))
        self.assertFalse(le.matches(['foo']))

    def test_labelexpr_not(self):
        le = LabelExpression('!this')
        self.assertEqual(le.tokens, [Token('NOT', '!'), Token('ID', 'this')])
        self.assertFalse(le.matches(['this']))
        self.assertTrue(le.matches(['that']))

    def test_labelexpr_and(self):
        le = LabelExpression('this&&that')
        les = LabelExpression('this && that')
        self.assertEqual(le.tokens, les.tokens)
        self.assertEqual(le.tokens, [Token('ID', 'this'), Token('AND', '&&'), Token('ID', 'that')])
        self.assertTrue(le.matches(['this', 'that']))
        self.assertFalse(le.matches(['this', 'foo']))
        self.assertFalse(le.matches(['that', 'foo']))
        self.assertFalse(le.matches(['this']))
        self.assertFalse(le.matches(['that']))
        self.assertFalse(le.matches(['foo']))

    def test_labelexpr_or(self):
        le = LabelExpression('this||that')
        self.assertEqual(le.tokens, [Token('ID', 'this'), Token('OR', '||'), Token('ID', 'that')])
        self.assertTrue(le.matches(['this', 'foo']))
        self.assertTrue(le.matches(['that', 'foo']))
        self.assertTrue(le.matches(['this', 'that']))
        self.assertFalse(le.matches(['foo']))
        self.assertTrue(le.matches(['this']))
        self.assertTrue(le.matches(['that']))

    def test_labelexpr_and_or(self):
        le = LabelExpression('this&&that||other')
        self.assertEqual(le.tokens, [Token('ID', 'this'), Token('AND', '&&'), Token('ID', 'that'),
                                     Token('OR', '||'), Token('ID', 'other')])
        self.assertTrue(le.matches(['other']))
        self.assertTrue(le.matches(['this', 'that']))
        self.assertFalse(le.matches(['this']))
        self.assertFalse(le.matches(['that']))
        self.assertFalse(le.matches(['foo']))

    def test_labelexpr_or_and(self):
        le = LabelExpression('this||that&&other')
        self.assertEqual(le.tokens, [Token('ID', 'this'), Token('OR', '||'), Token('ID', 'that'),
                                     Token('AND', '&&'), Token('ID', 'other')])
        self.assertTrue(le.matches(['this']))
        self.assertTrue(le.matches(['that', 'other']))
        self.assertFalse(le.matches(['other']))
        self.assertFalse(le.matches(['that']))
        self.assertFalse(le.matches(['foo']))

    def test_labelexpr_imply(self):
        le = LabelExpression('this->that')
        self.assertEqual(le.tokens, [Token('ID', 'this'), Token('IMPLY', '->'), Token('ID', 'that')])
        self.assertTrue(le.matches(['this', 'that']))
        self.assertTrue(le.matches(['other']))
        self.assertFalse(le.matches(['this']))
        self.assertTrue(le.matches(['that']))

    def test_labelexpr_and_imply(self):
        le = LabelExpression('this&&that->other')
        self.assertEqual(le.tokens, [Token('ID', 'this'), Token('AND', '&&'), Token('ID', 'that'),
                                     Token('IMPLY', '->'), Token('ID', 'other')])
        self.assertTrue(le.matches(['this', 'that', 'other']))
        self.assertTrue(le.matches(['other']))
        self.assertTrue(le.matches(['this']))
        self.assertTrue(le.matches(['that']))
        self.assertFalse(le.matches(['this', 'that']))

    def test_labelexpr_imply_and(self):
        le = LabelExpression('this->that&&other')
        self.assertEqual(le.tokens, [Token('ID', 'this'), Token('IMPLY', '->'), Token('ID', 'that'),
                                     Token('AND', '&&'), Token('ID', 'other')])
        self.assertTrue(le.matches(['this', 'that', 'other']))
        self.assertTrue(le.matches(['that', 'other']))
        self.assertFalse(le.matches(['this']))
        self.assertTrue(le.matches(['that']))
        self.assertTrue(le.matches(['other']))

    def test_labelexpr_onlyif(self):
        le = LabelExpression('this<->that')
        self.assertEqual(le.tokens, [Token('ID', 'this'), Token('ONLYIF', '<->'), Token('ID', 'that')])
        self.assertTrue(le.matches(['this', 'that']))
        self.assertTrue(le.matches(['foo', 'bar']))
        self.assertTrue(le.matches(['foo']))
        self.assertFalse(le.matches(['this']))
        self.assertFalse(le.matches(['that']))

    def test_labelexpr_and_onlylif(self):
        le = LabelExpression('this&&that<->other')
        self.assertEqual(le.tokens, [Token('ID', 'this'), Token('AND', '&&'), Token('ID', 'that'),
                                     Token('ONLYIF', '<->'), Token('ID', 'other')])
        self.assertTrue(le.matches(['this', 'that', 'other']))
        self.assertTrue(le.matches(['foo']))
        self.assertTrue(le.matches(['this']))
        self.assertTrue(le.matches(['that']))
        self.assertFalse(le.matches(['other']))
        self.assertFalse(le.matches(['this', 'that']))

    def test_labelexpr_onlyif_and(self):
        le = LabelExpression('this<->that&&other')
        self.assertEqual(le.tokens, [Token('ID', 'this'), Token('ONLYIF', '<->'), Token('ID', 'that'),
                                     Token('AND', '&&'), Token('ID', 'other')])
        self.assertTrue(le.matches(['this', 'that', 'other']))
        self.assertTrue(le.matches(['foo']))
        self.assertFalse(le.matches(['this']))
        self.assertTrue(le.matches(['that']))
        self.assertTrue(le.matches(['other']))
        self.assertFalse(le.matches(['this', 'that']))

    def test_labelexpr_all_ops_reverse(self):
        le = LabelExpression('a<->b->c||d&&!(e||f)')
        # Satisfies 'a<->b->c'
        self.assertTrue(le.matches(['a', 'b', 'c']))
        # d satisfies d&&!(e||f), so the expression becomes a<->b->False||True, a<->b->True, a<->True->True, a<->True
        # True<->True, True
        self.assertTrue(le.matches(['a', 'b', 'd']))
        # Satisfies 'a<->b->c'. The higher precedence -> operator allows c if b is not specified which in this case
        # results in True, and since a is True, these two match.
        self.assertTrue(le.matches(['a', 'c']))
        self.assertFalse(le.matches(['a', 'b']))
        self.assertFalse(le.matches(['d', 'e']))
        self.assertFalse(le.matches(['d', 'f']))
        self.assertFalse(le.matches(['d']))
        self.assertFalse(le.matches('e'))

if __name__ == '__main__':
    unittest.main()
