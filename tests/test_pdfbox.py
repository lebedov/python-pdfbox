#!/usr/bin/env python

from unittest import main, TestCase

import pdfbox

# To generate test PDF, process test.md with pandoc using the command
# pandoc -t latex test.md -o test.pdf
class test_pdfbox(TestCase):
    def test_extract(self):
        p = pdfbox.PDFBox()
        text = p.extract_text('test.pdf')
        self.assertEqual(text, 'this is a test PDF\n')

if __name__ == '__main__':
    main()
