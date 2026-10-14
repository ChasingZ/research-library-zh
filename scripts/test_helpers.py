"""Regression tests for observed translation and delivery failure modes."""
import json
import os
from pathlib import Path
import tempfile
import unittest
import zipfile

from audit_units import audit, numbers
from package_verified import package, sha256


class IntegrityTests(unittest.TestCase):
    def test_repeated_marker_missing(self):
        result = audit({'id': 'p', 'source': '@1@ and @1@', 'target': '@1@'})
        self.assertIn('placeholder_multiset_mismatch', result['issues'])

    def test_number_scale_corruption(self):
        result = audit({'id': 'p', 'source': '2.8B tokens.', 'target': '2.8亿词元。'})
        self.assertIn('visible_number_mismatch', result['issues'])

    def test_sentence_end_and_chinese_adjacent(self):
        result = audit({'id': 'p', 'source': 'Use 1.0. Cost 10k, rate 2.5e-3.',
                        'target': '采用1.0。成本10k，比例2.5e-3。'})
        self.assertEqual(result['issues'], [])

    def test_numbers_in_placeholders_not_compared(self):
        self.assertEqual(numbers('at @900@ and XXPH123XX'), {})

    def test_instruction_echo_and_verbatim(self):
        result = audit({'id': 'p', 'source': 'Prompt', 'target': '只输出译文', 'verbatim': True})
        self.assertIn('possible_instruction_echo', result['issues'])
        self.assertIn('verbatim_changed', result['issues'])

    def test_reorder_is_acceptable(self):
        result = audit({'id': 'p', 'source': '1,000 at @1@; 20% at @2@.',
                        'target': '@2@ 为20%，@1@ 为1,000。'})
        self.assertEqual(result['issues'], [])


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get('SKILL_TEST_TMPDIR'))
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.file = self.root / '阅读总结.md'
        self.file.write_text('摘要与方法总结', encoding='utf-8')
        (self.root / 'model.gguf').write_bytes(b'not a deliverable')
        self.data = {'files': [{'path': self.file.name, 'sha256': sha256(self.file),
                               'verified': True, 'evidence': 'reviewed source sections'}]}
        self.manifest = self.root / 'files.json'
        self.output = self.root / 'deliverables.zip'

    def run_package(self):
        self.manifest.write_text(json.dumps(self.data), encoding='utf-8')
        return package(self.manifest, self.output)

    def test_explicit_files_only(self):
        self.assertEqual(self.run_package(), 1)
        with zipfile.ZipFile(self.output) as archive:
            self.assertEqual(set(archive.namelist()), {'manifest.json', self.file.name})
            self.assertIsNone(archive.testzip())

    def test_modified_source_rejected(self):
        self.file.write_text('changed', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            self.run_package()
        self.assertFalse(self.output.exists())

    def test_unreviewed_rejected(self):
        self.data['files'][0]['verified'] = False
        with self.assertRaisesRegex(ValueError, 'verification'):
            self.run_package()

    def test_escape_rejected(self):
        self.data['files'][0]['path'] = '../outside.pdf'
        with self.assertRaisesRegex(ValueError, 'contained'):
            self.run_package()

    def test_existing_output_retained(self):
        self.output.write_bytes(b'existing')
        with self.assertRaisesRegex(ValueError, 'exists'):
            self.run_package()
        self.assertEqual(self.output.read_bytes(), b'existing')


if __name__ == '__main__':
    unittest.main()
