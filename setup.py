from __future__ import absolute_import
from setuptools import setup
import os


class PackageInfo(object):
    def __init__(self, info_file):
        with open(info_file) as f:
            exec(f.read(), self.__dict__)
        self.__dict__.pop('__builtins__', None)

    def __getattribute__(self, name):
        return super(PackageInfo, self).__getattribute__(name)

package_info = PackageInfo(os.path.join('pyqubo', 'package_info.py'))


install_requires = ['dimod>=0.7.4',
                    'numpy>=1.14.0,<2.0.0',
                    'six>=1.10.0,<2.0.0',
                    'dwave-neal>=0.4.2']

packages = ['pyqubo', 'pyqubo.core', 'pyqubo.utils']

python_requires = '>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*'

setup(
    name=package_info.__package_name__,
    version=package_info.__version__,
    description=package_info.__description__,
    long_description=open('README.rst').read(),
    author=package_info.__contact_names__,
    author_email=package_info.__contact_emails__,
    maintainer=package_info.__contact_names__,
    maintainer_email=package_info.__contact_emails__,
    url=package_info.__repository_url__,
    download_url=package_info.__download_url__,
    license=package_info.__license__,
    packages=packages,
    keywords=package_info.__keywords__,
    install_requires=install_requires,
    include_package_data=True,
    python_requires=python_requires,
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: Apache Software License',
    ],
)
