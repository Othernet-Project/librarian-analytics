import os
from setuptools import setup, find_packages

import librarian_analytics as pkg


def read(fname):
    """ Return content of specified file """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


VERSION = pkg.__version__

setup(
    name='librarian-analytics',
    version=VERSION,
    license='GPLv3',
    packages=[pkg.__name__],
    include_package_data=True,
    long_description=read('README.rst'),
    install_requires=[
        'bitpack',
        'user-agents',
        'bottle-fdsend',
        'bitarray',
        'librarian',
        'squery-pg'
    ],
    dependency_links=[		
        'git+ssh://git@github.com/Outernet-Project/librarian.git#egg=librarian-4.0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Applicaton',
        'Framework :: Bottle',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
