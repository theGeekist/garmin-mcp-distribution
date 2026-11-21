import unittest
from scripts.release_notes import release_notes

class ReleaseNotes(unittest.TestCase):
    def test_extracts_only_the_requested_version(self):
        source='# Changelog\n\n## 1.2.3\n\n- Public change.\n\n## 1.2.2\n\n- Older change.\n'
        self.assertEqual(release_notes(source,'1.2.3'),'- Public change.\n')
        self.assertEqual(release_notes(source,'1.2.2'),'- Older change.\n')
        for version in ('1.2.4','1.2.3\n## 9.9.9','01.2.3'):
            with self.assertRaises(ValueError):release_notes(source,version)
        with self.assertRaises(ValueError):release_notes(source+'\n## 1.2.3\n- duplicate\n','1.2.3')
        with self.assertRaises(ValueError):release_notes('## 1.2.3\n','1.2.3')
