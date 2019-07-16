#!/usr/bin/env python

from unittest import main, TestCase
from pathlib import Path
import pdfbox
import os
from sys import platform
# To generate test PDF, process test.md with pandoc using the command
# pandoc -t latex test.md -o test.pdf
from tempfile import TemporaryDirectory
class test_pdfbox(TestCase):
    def test_extract_text(self):
        p = pdfbox.PDFBox()
        text = p.extract_text('./test.pdf')
        if platform == "linux" or platform == "linux2" or platform == "darwin":
            self.assertEqual(text, 'this is a test PDF\n')
        elif platform == "win32":
            self.assertEqual(text, 'this is a test PDF\r\n')

    def test_pdf_to_images(self):
        p = pdfbox.PDFBox()

        with TemporaryDirectory() as output_dir:
            output_prefix = (Path(output_dir) / 'test').resolve()
            result = p.pdf_to_images('./test2.pdf', outputPrefix=output_prefix)
            self.assertTrue('test1.jpg' in os.listdir(output_dir) and 'test2.jpg' in os.listdir(output_dir))

    def test_extract_images(self):
        p = pdfbox.PDFBox()

        with TemporaryDirectory() as output_dir:
            output_prefix = (Path(output_dir) / 'test').resolve()
            result = p.extract_images('./test3.pdf', prefix=output_prefix)
            self.assertTrue('test-1.png' in os.listdir(output_dir))


if __name__ == '__main__':
    main()
