from io import StringIO
from unittest import TestCase

from xlrd.compdoc import CompDoc, CompDocError, EOCSID


class TestOversizedStream(TestCase):
    def locate(self, sectors):
        doc = object.__new__(CompDoc)
        doc.seen = [0] * len(sectors)
        doc.ignore_workbook_corruption = False
        doc.logfile = StringIO()
        return doc._locate_stream(b'aaaabbbbcccc', 0, sectors, 4, 0, 4, 'Workbook', 6)

    def test_contiguous_extra_sector(self):
        data, offset, size = self.locate([1, EOCSID])
        self.assertEqual(data[offset:offset + size], b'aaaa')
        self.assertEqual(size, 4)

    def test_fragmented_extra_sector(self):
        data, offset, size = self.locate([2, EOCSID, EOCSID])
        self.assertEqual(data, b'aaaacccc')
        self.assertEqual(data[offset:offset + size], b'aaaa')
        self.assertEqual(size, 4)

    def test_repeated_sector_still_fails(self):
        with self.assertRaisesRegex(CompDocError, 'corruption: seen'):
            self.locate([0])
