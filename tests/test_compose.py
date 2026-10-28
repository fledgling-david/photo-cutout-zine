import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image, ImageChops, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('compose_zine', ROOT / 'scripts/compose_zine.py')
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class CompositionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        im = Image.new('RGB', (900, 600))
        im.putdata([((x * 19 + y) % 256, (y * 7) % 256, (x + y * 3) % 256)
                    for y in range(600) for x in range(900)])
        self.source = self.base / 'source.png'
        im.save(self.source)
        self.config = json.loads((ROOT / 'examples/demo-config.json').read_text('utf-8'))

    def tearDown(self):
        self.tmp.cleanup()

    def test_layout_and_real_crop_reuse(self):
        out = self.base / 'zine.png'
        info = M.compose(self.source, self.config, out, width=600)
        self.assertEqual(info['size'], [600, 800])
        self.assertEqual(info['pixel_verification'], 'passed')
        a, b = info['upper_box'], info['lower_box']
        self.assertEqual(a[0] + a[2], 600)
        self.assertEqual(a[1] + a[3], 400)
        self.assertEqual(b, [a[0], a[1] + 400, a[2], a[3] + 400])
        with Image.open(self.source) as src, Image.open(out) as got:
            top = ImageOps.fit(src.convert('RGB'), (600, 400), method=M.RESAMPLE)
            mask = M.perforation_mask((a[2]-a[0], a[3]-a[1]), 600)
            opaque = mask.point(lambda v: 255 if v == 255 else 0)
            M.same_under_mask(got.crop(b), top.crop(a), opaque, 'saved stamp')
            expected = top.copy()
            expected.paste(M.paper((600, 800)).crop(a), a[:2], mask)
            self.assertIsNone(ImageChops.difference(got.crop((0, 0, 600, 400)), expected).getbbox())

    def test_source_and_existing_output_are_protected(self):
        with self.assertRaisesRegex(ValueError, 'source'):
            M.compose(self.source, self.config, self.source, width=600)
        out = self.base / 'existing.png'
        out.write_bytes(b'existing')
        with self.assertRaisesRegex(ValueError, 'already exists'):
            M.compose(self.source, self.config, out, width=600)
        self.assertEqual(out.read_bytes(), b'existing')

    def test_invalid_date_is_rejected(self):
        self.config['date'] = '02. 30. 2026'
        with self.assertRaisesRegex(ValueError, 'real date'):
            M.validate_config(self.config)


if __name__ == '__main__':
    unittest.main()
