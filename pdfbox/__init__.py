#!/usr/bin/python3

"""
Python interface to Apache PDFBox.
"""

import hashlib
import os
import shutil
import urllib.request

import appdirs
import sarge

pdfbox_version = '2.0.8'
pdfbox_url = 'https://www.apache.org/dist/pdfbox/{version}/pdfbox-app-{version}.jar'.format(version=pdfbox_version)
md5_url = 'https://www.apache.org/dist/pdfbox/{version}/pdfbox-app-{version}.jar.md5'.format(version=pdfbox_version)

class PDFBox(object):
    """
    Python interface to Apache PDFBox.

    Methods
    -------
    extract_text(input_path, output_path='',
                 password=None, encoding=None, html=False, sort=False,
                 ignore_beads=False, force=False, start_page=1, end_page=None)
        Extract all text from PDF file.
    """

    def _verify_md5(self, data, digest):
        """
        Verify MD5 checksum.
        """
        
        return hashlib.md5(data).hexdigest() == digest

    def _get_pdfbox_path(self):
        """
        Return path to local copy of PDFBox jar file.
        """

        # Use PDFBOX environmental variable if it exists:
        if 'PDFBOX' in os.environ:        
            pdfbox_path = os.environ['PDFBOX']
            if not os.path.exists(pdfbox_path):
                raise RuntimeError('pdfbox not found')
            return pdfbox_path

        # Use platform-specific cache directory:
        a = appdirs.AppDirs('python-pdfbox')
        cache_dir = a.user_cache_dir    
        pdfbox_path = os.path.join(cache_dir, os.path.basename(pdfbox_url))

        # Retrieve, cache, and verify PDFBox jar file:
        if not os.path.exists(pdfbox_path):    
            r = urllib.request.urlopen(pdfbox_url)
            try:
                data = r.read()
            except:
                raise RuntimeError('error retrieving %s' % os.path.basename(pdfbox_url))
            else:
                if not os.path.isdir(cache_dir):
                    os.mkdir(cache_dir)
                with open(pdfbox_path, 'wb') as f:
                    f.write(data)

            r = urllib.request.urlopen(md5_url)
            encoding = r.headers.get_content_charset('utf-8')
            try:
                md5 = r.read().decode(encoding).strip()
            except:
                raise RuntimeError('error retrieving md5sum')
            else:
                if not self._verify_md5(data, md5):
                    raise RuntimeError('failed to verify md5sum')

        return pdfbox_path
    
    def __init__(self):
        self.pdfbox_path = self._get_pdfbox_path()
        self.java_path = shutil.which('java')
        if not self.java_path:
            raise RuntimeError('java not found')

    def extract_text(self, input_path, output_path='',
                     password=None, encoding=None, html=False, sort=False,
                     ignore_beads=False, force=False, start_page=1, end_page=None):
        """
        Extract all text from PDF file.

        Parameters
        ----------
        input_path : str
            Input PDF file.
        output_path : str
            Output text file. If not specified, the extracted text is returned.
        password : str
            PDF password.
        encoding : str
            Text file encoding.
        html : bool
            If True, extract as HTML.
        sort : bool
            If True, sort text before returning it.
        ignore_beads : bool
            If True, ignore separation by beads.
        force : bool
            If True, ignore corrupt objects.
        start_page : int
            First page to extract (starting with 1).
        end_page : int
            Last page to extract (starting with 1).

        Returns
        -------
        text : str
            Extracted text. If `output_path` is not specified, nothing is returned.
        """
        
        options = (' -password {password}'.format(password=password) if password else '') +\
                  (' -encoding {encoding}'.format(encoding=encoding) if encoding else '') +\
                  (' -html' if html else '') +\
                  (' -sort' if sort else '') +\
                  (' -ignoreBeads' if ignore_beads else '') +\
                  (' -force' if force else '') +\
                  (' -startPage {start_page}'.format(start_page=start_page) if start_page else '') +\
                  (' -endPage {end_page}'.format(end_page=end_page) if end_page else '')
        if not output_path:
            options += ' -console'
        cmd = '{java_path} -jar {pdfbox_path} ExtractText {options} {input_path} {output_path}'.format(java_path=self.java_path,
                                                                                                       pdfbox_path=self.pdfbox_path,
                                                                                                       options=options,
                                                                                                       input_path=input_path,
                                                                                                       output_path=output_path)
        p = sarge.capture_stdout(cmd)
        if not output_path:
            return p.stdout.text
