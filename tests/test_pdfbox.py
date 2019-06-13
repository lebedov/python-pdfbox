#!/usr/bin/env python

from unittest import main, TestCase

import pdfbox
import os
# To generate test PDF, process test.md with pandoc using the command
# pandoc -t latex test.md -o test.pdf
class test_pdfbox(TestCase):
    def test_extract(self):
        p = pdfbox.PDFBox()
        text = p.extract_text('tests/test.pdf')
        self.assertEqual(text, 'this is a test PDF\r\n')

    def test_image_extract(self):
        p = pdfbox.PDFBox()
        output_prefix = r'tests/output/test'
        result = p.pdf_to_images('tests/test2.pdf', outputPrefix=output_prefix)
        self.assertTrue('test1.jpg' in os.listdir('tests/output') and 'test2.jpg' in os.listdir('tests/output'))

if __name__ == '__main__':
    main()
