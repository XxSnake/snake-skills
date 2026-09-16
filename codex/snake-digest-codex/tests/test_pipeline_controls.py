import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))

import md_to_pdf
import verify_digest_pdf


class PipelineControlsTest(unittest.TestCase):
    def test_explicit_missing_cover_fails(self) -> None:
        with self.assertRaises(FileNotFoundError):
            md_to_pdf.md_to_html('# 标题\n\n正文', cover_image='missing-cover.png')

    def test_failed_browser_render_never_reuses_old_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            html = root / 'input.html'
            html.write_text('<p>test</p>', encoding='utf-8')
            output = root / 'existing.pdf'
            old = b'old-pdf' * 300
            output.write_bytes(old)
            with patch.object(md_to_pdf, 'find_browser', return_value=root / 'browser.exe'), patch.object(
                md_to_pdf.subprocess,
                'run',
                return_value=subprocess.CompletedProcess([], 1, '', 'render failed'),
            ):
                with self.assertRaises(RuntimeError):
                    md_to_pdf.render_pdf_with_browser(html, output)
            self.assertEqual(output.read_bytes(), old)

    def test_page_size_css_and_page_selection(self) -> None:
        html = md_to_pdf.md_to_html('# 标题\n\n正文', page_size='A5', css_overrides='body { color: #123456; }')
        self.assertIn('size: A5;', html)
        self.assertIn('width: 148mm;', html)
        self.assertIn('"Noto Serif SC"', html)
        self.assertIn('#123456', html)
        self.assertEqual(verify_digest_pdf.parse_pages('1,3-4', 5), [1, 3, 4])

    def test_custom_style_and_two_heroes_pass_but_layout_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            images = root / 'images'
            images.mkdir()
            specs = [('img_cover', (900, 1200)), ('img_01', (1200, 900)), ('img_02', (1200, 900))]
            for index, (name, size) in enumerate(specs):
                image = Image.effect_noise(size, 70 + index).convert('RGB')
                image.save(images / f'{name}.png')
            article = root / 'article.md'
            article.write_text(
                '# 标题\n\n正文。\n\n<!--IMG:img_01:图一:hero-->\n\n<!--IMG:img_02:图二:hero-->'
                '\n\n## 资料来源与延伸阅读\n\n- https://example.com/source\n',
                encoding='utf-8',
            )
            (root / 'sources.md').write_text(
                '# 来源\n\n- 标题：测试来源\n- URL：https://example.com/source\n- 发布日期：2026-09-17\n'
                '- 支撑事实：这是一段足够长的测试来源记录，用来验证严格检查确实要求真实链接，而不是只计算字符数量。\n'
                '- 可信度备注：测试夹具，不作为真实知识来源。\n',
                encoding='utf-8',
            )
            plan = {
                'generation_mode': 'chatgpt-image-model-raster-only',
                'style_profile': 'custom',
                'style': 'cool blue and white editorial illustration',
                'max_body_hero': 2,
                'images': [
                    {'id': 'img_cover', 'filename': 'img_cover.png', 'role': 'cover', 'layout': 'cover', 'orientation': 'portrait', 'prompt_en': 'portrait cover'},
                    {'id': 'img_01', 'filename': 'img_01.png', 'role': 'body', 'layout': 'hero', 'orientation': 'landscape', 'prompt_en': 'cool scene one'},
                    {'id': 'img_02', 'filename': 'img_02.png', 'role': 'body', 'layout': 'normal', 'orientation': 'landscape', 'prompt_en': 'cool scene two'},
                ],
            }
            plan_path = root / 'image_plan.json'
            plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding='utf-8')
            command = [sys.executable, str(SCRIPTS / 'validate_digest.py'), str(article), str(plan_path), str(images), '--strict']
            failed = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('layout mismatch for img_02', failed.stdout)
            plan['images'][2]['layout'] = 'hero'
            plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding='utf-8')
            passed = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)


if __name__ == '__main__':
    unittest.main()
