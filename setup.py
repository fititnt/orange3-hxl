#!/usr/bin/env python

from os import path, walk

import sys
from setuptools import setup, find_packages

NAME = "Orange3-HXLvisualETL"

VERSION = "0.3.0rc1"

AUTHOR = 'EticaAI'
AUTHOR_EMAIL = 'rocha@ieee.org'

URL = 'https://github.com/fititnt/orange3-hxl'
DESCRIPTION = """
Humanitarian Exchange Language (HXL) visual Extract, Transform, Load (ETL)
is an add-on for Orange Data Mining.
"""
# LONG_DESCRIPTION = open(path.join(path.dirname(__file__), 'README.pypi'),
#                         'r', encoding='utf-8').read()
LONG_DESCRIPTION = open(path.join(path.dirname(__file__), 'README.md'),
                        'r', encoding='utf-8').read()

LICENSE = "Unlicence"

KEYWORDS = (
    # [PyPi](https://pypi.python.org) packages with keyword "orange3 add-on"
    # can be installed using the Orange Add-on Manager
    'orange3 add-on',
    'hxl',
)

PACKAGES = find_packages()

PACKAGE_DATA = {
    'orangecontrib.hxl': ['tutorials/*.ows'],
    'orangecontrib.hxl.widgets': ['icons/*'],
    'orangecontrib.referencedata.widgets': ['icons/*'],
}

DATA_FILES = [
    # Data files that will be installed outside site-packages folder
]

INSTALL_REQUIRES = [
    'Orange3',
]

ENTRY_POINTS = {
    # Entry points that marks this package as an orange add-on. If set, addon will
    # be shown in the add-ons manager even if not published on PyPi.
    'orange3.addon': (
        'Orange3-HXLvisualETL = orangecontrib.hxl',
        # 'hxl = orangecontrib.hxl',
    ),
    # Entry point used to specify packages containing tutorials accessible
    # from welcome screen. Tutorials are saved Orange Workflows (.ows files).
    'orange.widgets.tutorials': (
        # Syntax: any_text = path.to.package.containing.tutorials
        'hxltutorials = orangecontrib.hxl.tutorials',
    ),

    # Entry point used to specify packages containing widgets.
    'orange.widgets': (
        # Syntax: category name = path.to.package.containing.widgets
        # Widget category specification can be seen in
        #    orangecontrib/hxl/widgets/__init__.py
        # 'HXL visual ETL = orangecontrib.hxl.widgets',
        'Orange3-HXLvisualETL = orangecontrib.hxl.widgets',
        # 'HXL Reference Data = orangecontrib.referencedata.widgets',
        'Orange3-HXLReferenceData = orangecontrib.referencedata.widgets',
    ),

    # Register widget help
    "orange.canvas.help": (
        'html-index = orangecontrib.hxl.widgets:WIDGET_HELP_PATH',)
}

NAMESPACE_PACKAGES = ["orangecontrib"]

TEST_SUITE = "orangecontrib.hxl.tests.suite"


def include_documentation(local_dir, install_dir):
    global DATA_FILES
    if 'bdist_wheel' in sys.argv and not path.exists(local_dir):
        print("Directory '{}' does not exist. "
              "Please build documentation before running bdist_wheel."
              .format(path.abspath(local_dir)))
        sys.exit(0)

    doc_files = []
    for dirpath, dirs, files in walk(local_dir):
        doc_files.append((dirpath.replace(local_dir, install_dir),
                          [path.join(dirpath, f) for f in files]))
    DATA_FILES.extend(doc_files)


if __name__ == '__main__':
    include_documentation('doc/_build/html', 'help/orange3-example')
    setup(
        name=NAME,
        version=VERSION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type='text/markdown',
        license=LICENSE,
        packages=PACKAGES,
        package_data=PACKAGE_DATA,
        data_files=DATA_FILES,
        install_requires=INSTALL_REQUIRES,
        entry_points=ENTRY_POINTS,
        keywords=KEYWORDS,
        namespace_packages=NAMESPACE_PACKAGES,
        zip_safe=False,
    )
