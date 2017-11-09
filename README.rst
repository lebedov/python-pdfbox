.. -*- rst -*-

python-pdfbox
=============

Package Description
-------------------
Provides a simple Python interface to the `Apache PDFBox <https://pdfbox.apache.org/>`_
command-line tools.

Installation
------------
The package may be installed as follows: ::

    pip install python-pdfbox

One may specify the location of the PDFBox jar file via the `PDFBOX`
environmental variable. If not set, python-pdfbox looks for the jar file
in the platform-specific user cache directory and automatically downloads
and caches it if not present.

Usage
-----
The interface currently exposes the text extraction feature of PDFBox only: ::

    import pdfbox
    p = pdfbox.PDFBox()
    text = p.extract_text('/path/to/my_file.pdf')
    
Development
-----------
The latest release of the package may be obtained from
`GitHub <https://github.com/lebedov/python-pdfbox>`_.

Author
------
See the included `AUTHORS.rst 
<https://github.com/lebedov/python-pdfbox/blob/master/AUTHORS.rst>`_ file for more 
information.

License
-------
This software is licensed under the
`Apache 2.0 License <https://opensource.org/licenses/Apache-2.0>`_.
See the included `LICENSE.rst 
<https://github.com/lebedov/python-pdfbox/blob/master/LICENSE.rst>`_ file for more 
information.
