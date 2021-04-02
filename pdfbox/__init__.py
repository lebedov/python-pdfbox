#!/usr/bin/python3

"""
Python interface to Apache PDFBox.
"""

import hashlib
import html.parser
import os
import pathlib
import re
import shutil
import urllib.request

import appdirs
import jpype
import jpype.imports
import pkg_resources

pdfbox_archive_url = 'https://archive.apache.org/dist/pdfbox/'

class _PDFBoxVersionsParser(html.parser.HTMLParser):
    """
    Class for parsing versions available on PDFBox archive site.
    """

    def feed(self, data):
        self.result = []
        super(_PDFBoxVersionsParser, self).feed(data)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for a in attrs:
                if a[0] == 'href':
                    s = a[1].strip('/')
                    if re.search('\d+\.\d+\.\d+.*', s):
                        self.result.append(s)

class PDFBox(object):
    """
    Python interface to Apache PDFBox.

    Methods
    -------
    extract_text(input_path, output_path='',
                 password=None, encoding=None, html=False, sort=False,
                 ignore_beads=False, start_page=1, end_page=None)
        Extract all text from PDF file.
    pdf_to_images(input_path, password=None,
                  imageType=None, outputPrefix=None,
                  startPage=None, endPage=None,
                  page=None, dpi=None, color=None, cropbox=None, time=True)
        Extract all pages of PDF file as images.
    extract_images(input_path, password=None, prefix=None,
                   directJPEG=False)
        Extract all images from a PDF file.
    """

    def _verify_sha512(self, data, digest):
        """
        Verify SHA512 checksum.
        """

        return hashlib.sha512(data).hexdigest() == digest

    def _get_latest_pdfbox_url(self):
        r = urllib.request.urlopen(pdfbox_archive_url)
        try:
            data = r.read()
        except:
            raise RuntimeError('error retrieving %s' % pdfbox_archive_url)
        else:
            data = data.decode('utf-8')
        p = _PDFBoxVersionsParser()
        p.feed(data)

        # Temporarily disallow PDFBox 3 because of change in command line
        # interface:
        versions = list(filter(lambda v: pkg_resources.parse_version(v).major<3,
                               p.result))
        latest_version = sorted(versions, key=pkg_resources.parse_version)[-1]
        return pdfbox_archive_url + latest_version + '/pdfbox-app-' + \
            latest_version + '.jar'

    def _get_pdfbox_path(self):
        """
        Return path to local copy of PDFBox jar file.
        """

        # Use PDFBOX environmental variable if it exists:
        if 'PDFBOX' in os.environ:
            pdfbox_path = pathlib.Path(os.environ['PDFBOX'])
            if not pdfbox_path.exists():
                raise RuntimeError('pdfbox not found')
            return pdfbox_path

        # Use platform-specific cache directory:
        a = appdirs.AppDirs('python-pdfbox')
        cache_dir = pathlib.Path(a.user_cache_dir)

        # Try to find pdfbox-app-*.jar file with most recent version in cache directory:
        file_list = list(cache_dir.glob('pdfbox-app-*.jar'))
        if file_list:
            def f(s):
                v = re.search('pdfbox-app-([\w\.\-]+)\.jar', s.name).group(1)
                return pkg_resources.parse_version(v)
            return sorted(file_list, key=f)[-1]
        else:
            # If no jar files are cached, find the latest version jar, retrieve it,
            # cache it, and verify its checksum:
            pdfbox_url = self._get_latest_pdfbox_url()
            sha512_url = pdfbox_url + '.sha512'
            r = urllib.request.urlopen(pdfbox_url)
            try:
                data = r.read()
            except:
                raise RuntimeError('error retrieving %s' % pdfbox_url)
            else:
                if not os.path.exists(cache_dir.as_posix()):
                    cache_dir.mkdir(parents=True)
                pdfbox_path = cache_dir.joinpath(pathlib.Path(pdfbox_url).name)
                with open(pdfbox_path.as_posix(), 'wb') as f:
                    f.write(data)

            r = urllib.request.urlopen(sha512_url)
            encoding = r.headers.get_content_charset('utf-8')
            try:
                sha512 = r.read().decode(encoding).strip()
            except:
                raise RuntimeError('error retrieving sha512sum')
            else:
                if not self._verify_sha512(data, sha512):
                    raise RuntimeError('failed to verify sha512sum')

            return pdfbox_path

    def __init__(self):
        self.pdfbox_path = self._get_pdfbox_path()
        jpype.addClassPath(self.pdfbox_path)
        if not jpype.isJVMStarted():
            jpype.startJVM(convertStrings=False)
        import org.apache.pdfbox.tools as tools
        self.pdfbox_tools = tools

    def extract_text(self, input_path, output_path='',
                     password=None, encoding=None, html=False, sort=False,
                     ignore_beads=False, start_page=1, end_page=None, console=False):
        """
        Extract all text from PDF file.

        Parameters
        ----------
        input_path : str
            Input PDF file.
        output_path : str
            Output text file. If not specified, the extracted text is written to
            a text file with the same basename as the input file.
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
        start_page : int
            First page to extract (starting with 1).
        end_page : int
            Last page to extract (starting with 1).
        console : bool
            If True, write output to console.
        """

        options = []
        if password:
            options.extend(['-password', password])
        if encoding:
            options.extend(['-encoding', encoding])
        if html:
            options.append('-html')
        if sort:
            options.append('-sort')
        if ignore_beads:
            options.append('-ignoreBeads')
        if start_page:
            options.extend(['-startPage', str(start_page)])
        if end_page:
            options.extend(['-endPage', str(end_page)])
        if console:
            options.append('-console')

        args = options
        args.append(str(pathlib.Path(input_path).expanduser()))
        if output_path:
            args.append(str(pathlib.Path(output_path).expanduser()))
        self.pdfbox_tools.ExtractText.main(args)

    def pdf_to_images(self, input_path, password=None,
                      imageType=None, outputPrefix=None,
                      startPage=None, endPage=None,
                      page=None, dpi=None, color=None, cropbox=None,time=True):
        """
        Extract all pages of PDF file as images.

        Parameters
        ----------
        input_path : str
            Input PDF file.
        password : str
            PDF password.
        imageType : str
            The image type to write to. Currently only jpg or png (default:
            jpg).
        outputPrefix : str
            The prefix to the image file (default: name of PDF document).
            e.g
                >> outputPrefix = '/output/': Images saved in `output` directory
                as 1.jpg, 2.jpg, etc.
                >> outputPrefix = '/output' : Images saved in `output` directory
                as output1.jpg, output2.jpg, etc.
                in the same location where the input file is.
        startPage : bool
            The first page to convert, one-based (default: 1).
        endPage : bool
            The last page to convert, one-based (default: last).
        page : int
            The only page to extract, one-based.
        dpi : int
            DPI resolution of exported images (default:
            detected from screen, or 96 if headless).
        color : str
            The color depth; may be set to `bilevel`, `gray`, `rgb`, `rgba`
            (default: `rgb`)
        cropbox : str
            The page area to export, e.g "34 45 56 67"
        time : int
            Prints timing information to stdout.
        """

        options = []
        if password:
            options.extend(['-password', password])
        if imageType:
            options.extend(['-imageType', imageType])
        if outputPrefix:
            options.extend(['-outputPrefix', str(pathlib.Path(outputPrefix).expanduser())])
        if startPage:
            options.extend(['-startPage', str(startPage)])
        if endPage:
            options.extend(['-endPage', str(endPage)])
        if page:
            options.extend(['-page', str(page)])
        if dpi:
            options.extend(['-dpi', str(dpi)])
        if color:
            options.extend(['-color', str(color)])
        if cropbox:
            options.extend(['-cropbox', str(cropbox)])
        if time:
            options.append('-time')

        args = options
        args.append(str(pathlib.Path(input_path).expanduser()))
        self.pdfbox_tools.PDFToImage.main(args)

    def extract_images(self, input_path, password=None, prefix=None, directJPEG=False):
        """
        Extract all images from a PDF file.

        Parameters
        ----------
        input_path : str
            Input PDF file.
        password : str
            PDF password.
        prefix : str
            The prefix to the image file (default: name of PDF document).
        directJPEG: bool
            Forces the direct extraction of JPEG images regardless of colorspace (default: False).
        """

        options = []
        if password:
            options.extend(['-password', password])
        if prefix:
            options.extend(['-prefix', str(pathlib.Path(prefix).expanduser())])
        if directJPEG:
            options.extend(['-directJPEG', directJPEG])

        args = options
        args.append(str(pathlib.Path(input_path).expanduser()))
        self.pdfbox_tools.ExtractImages.main(args)
