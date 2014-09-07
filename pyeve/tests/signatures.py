__author__ = 'Rudy'

import unittest
import decimal

from pyeve.signatures import parseSignatures, combineSignatures, Signature, unparseSignatures


class SignaturesParsingTestCase(unittest.TestCase):
    def test_simpleParse(self):
        sigData = """SNL-720	Cosmic Signature	Relic Site	Ruined Serpentis Temple Site	100,00%	50,99 AU
KKP-634	Cosmic Signature	Data Site		0,00%	62,23 AU
JVY-655	Cosmic Signature	Combat Site		0,00%	50,02 AU"""

        result = parseSignatures(sigData)

        self.assertEqual(len(result), 3)

        sigByKey = dict([(x.key, x) for x in result])

        self.assertIn('SNL-720', sigByKey)
        self.assertIn('KKP-634', sigByKey)
        self.assertIn('JVY-655', sigByKey)

        self.assertEqual(sigByKey['SNL-720'], Signature('SNL-720', 'Cosmic Signature', 'Relic Site',
                                                        'Ruined Serpentis Temple Site'))

        self.assertEqual(sigByKey['KKP-634'], Signature('KKP-634', 'Cosmic Signature', 'Data Site', ''))

        self.assertEqual(sigByKey['JVY-655'], Signature('JVY-655', 'Cosmic Signature', 'Combat Site', ''))

    def test_parseEmpty(self):
        result = parseSignatures("")

        self.assertEqual(len(result), 0)

    def test_parseEmptyNewline(self):
        result = parseSignatures("\n")

        self.assertEqual(len(result), 0)

    def test_unparseSignatures(self):
        signatures = [
            Signature('JVY-655', 'Cosmic Signature', 'Combat Site', 'ala'),
            Signature('ZXC-123', '', 'def', 'ghi'),
            Signature('ABC-456', 'Lorem ipsum', 'Dolor sit', 'Amet est'),
        ]

        signaturesStr = unparseSignatures(signatures)

        self.assertIn("JVY-655\tCosmic Signature\tCombat Site\tala", signaturesStr)
        self.assertIn("ZXC-123\t\tdef\tghi", signaturesStr)
        self.assertIn("ABC-456\tLorem ipsum\tDolor sit\tAmet est", signaturesStr)

    def test_unparseParseEqual(self):
        signatures = [
            Signature('JVY-655', 'Cosmic Signature', 'Combat Site', 'ala'),
            Signature('ZXC-123', '', 'def', 'ghi'),
            Signature('ABC-456', 'Lorem ipsum', 'Dolor sit', 'Amet est'),
        ]

        signaturesStr = unparseSignatures(signatures)

        parsed = parseSignatures(signaturesStr)

        self.assertEqual(len(parsed), len(signatures))

        self.assertIn(signatures[0], parsed)
        self.assertIn(signatures[1], parsed)
        self.assertIn(signatures[2], parsed)


class SignatureUpdatingTestCase(unittest.TestCase):
    def test_simpleUpdate(self):
        oldSignatures = [
            Signature('JVY-655', '', '', ''),
            Signature('ZXC-123', 'abc', 'def', ''),
        ]

        newSignatures = [
            Signature('JVY-655', 'Cosmic Signature', 'Combat Site', 'ala'),
            Signature('ZXC-123', '', 'def', 'ghi'),
        ]

        result = combineSignatures(oldSignatures, newSignatures)

        self.assertEqual(len(result), 2)

        sigByKey = dict([(x.key, x) for x in result])

        self.assertIn('JVY-655', sigByKey)
        self.assertIn('ZXC-123', sigByKey)

        self.assertEqual(sigByKey['JVY-655'], Signature('JVY-655', 'Cosmic Signature', 'Combat Site', 'ala'))

        self.assertEqual(sigByKey['ZXC-123'], Signature('ZXC-123', 'abc', 'def', 'ghi'))

    def test_dropOld(self):
        oldSignatures = [
            Signature('ABC-123', '', '', ''),
            Signature('ABC-456', '', '', ''),
            Signature('DEF-789', '', '', ''),
            Signature('ZXC-123', 'abc', 'def', ''),
        ]

        newSignatures = [
            Signature('ABC-123', '', '', ''),
            Signature('ZXC-123', 'abc', 'def', ''),
        ]

        result = combineSignatures(oldSignatures, newSignatures)

        self.assertEqual(len(result), 2)

        sigByKey = dict([(x.key, x) for x in result])

        self.assertIn('ABC-123', sigByKey)
        self.assertIn('ZXC-123', sigByKey)

        self.assertNotIn('ABC-456', sigByKey)
        self.assertNotIn('DEF-789', sigByKey)

    def test_addNew(self):
        oldSignatures = [
            Signature('ABC-123', '', '', ''),
            Signature('ZXC-123', 'abc', 'def', ''),
        ]

        newSignatures = [
            Signature('ABC-123', '', '', ''),
            Signature('ABC-456', '', '', ''),
            Signature('DEF-789', '', '', ''),
            Signature('ZXC-123', 'abc', 'def', ''),
        ]

        result = combineSignatures(oldSignatures, newSignatures)

        self.assertEqual(len(result), 4)

        sigByKey = dict([(x.key, x) for x in result])

        self.assertIn('ABC-123', sigByKey)
        self.assertIn('ABC-456', sigByKey)
        self.assertIn('DEF-789', sigByKey)
        self.assertIn('ZXC-123', sigByKey)

