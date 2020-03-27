#!/usr/bin/env python

from unittest import main, TestCase
from pathlib import Path
import pdfbox
import os
from tempfile import TemporaryDirectory

# To generate test PDF, process test.md with pandoc using the command
# pandoc -t latex test.md -o test.pdf

class test_pdfbox(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = pdfbox.PDFBox()

    def test_init_multiple(self):
        # Try to initialize and use a second 
        # instance of the class:
        p2 = pdfbox.PDFBox()

    def test_extract_text(self):
        with TemporaryDirectory() as output_dir:
            output_path = (Path(output_dir) / 'test.txt').resolve()
            self.p.extract_text('./test.pdf', output_path)
            self.assertTrue('test.txt' in os.listdir(output_dir))

    def test_extract_text_input_with_spaces(self):
        with TemporaryDirectory() as output_dir:
            output_path = (Path(output_dir) / 'test space.txt').resolve()
            self.p.extract_text('./test space.pdf', output_path)
            print(os.listdir(output_dir))
            self.assertTrue('test space.txt' in os.listdir(output_dir))

    def test_pdf_to_images(self):
        with TemporaryDirectory() as output_dir:
            output_prefix = (Path(output_dir) / 'test').resolve()
            self.p.pdf_to_images('./test2.pdf', outputPrefix=output_prefix)
            self.assertTrue('test1.jpg' in os.listdir(output_dir) and 'test2.jpg' in os.listdir(output_dir))

    def test_extract_images(self):
        with TemporaryDirectory() as output_dir:
            output_prefix = (Path(output_dir) / 'test').resolve()
            self.p.extract_images('./test3.pdf', prefix=output_prefix)
            self.assertTrue('test-1.png' in os.listdir(output_dir))

if __name__ == '__main__':
    main()
