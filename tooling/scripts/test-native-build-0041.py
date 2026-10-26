"""Small regression checks for configuration and stale-build rejection; no compiler/device."""
from pathlib import Path
import json
import tempfile
import unittest
import native_build_0041 as native


class BuildChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / 'app.cpp'
        self.source.write_text('// app\n')
        self.obj = self.root / 'app.o'
        self.obj.write_bytes(b'compiled object')
        self.config = self.root / 'app.json'
        native.write_json(self.config, {'format': 1, 'root': '.', 'include_dirs': ['.'],
            'defines': [], 'plain_sources': [], 'sources': ['app.cpp']})
        self.audit = {'passed': True, 'objects': [{'file': str(self.obj), 'sha256': native.sha(self.obj),
            'source': str(self.source), 'source_sha256': native.sha(self.source)}], 'input_headers': [],
            'app_config': {'path': str(self.config), 'sha256': native.sha(self.config)}}
        native.write_json(self.root / 'native-core-audit.json', self.audit)

    def tearDown(self):
        self.temp.cleanup()

    def test_source_only_configuration(self):
        config = native.read_app_config(self.config)
        self.assertEqual(config['sources'], [self.source.resolve()])
        self.assertTrue(native.validate_audit(self.root)['passed'])

    def test_configuration_cannot_add_external_sources(self):
        config = json.loads(self.config.read_text())
        config['sources'] = ['../outside.cpp']
        native.write_json(self.config, config)
        with self.assertRaisesRegex(ValueError, 'within its source root'):
            native.read_app_config(self.config)

    def test_changed_source_object_or_config_invalidates_link(self):
        for path in (self.source, self.obj, self.config):
            with self.subTest(path=path.name):
                original = path.read_bytes()
                path.write_bytes(original + b' ')
                native.write_json(self.root / 'native-link-report.json', {'linked': True})
                with self.assertRaisesRegex(ValueError, 'changed'):
                    native.link(self.root, 'compiler-must-not-run-')
                self.assertFalse(json.loads((self.root / 'native-link-report.json').read_text())['linked'])
                path.write_bytes(original)


if __name__ == '__main__':
    unittest.main()
