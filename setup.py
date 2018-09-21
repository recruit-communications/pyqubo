from __future__ import absolute_import
from setuptools import setup

install_requires = ['dimod>=0.7.4',
                    'numpy>=1.14.0,<2.0.0',
                    'six>=1.10.0,<2.0.0']

packages = ['pyqubo', 'pyqubo.core', 'pyqubo.utils']

python_requires = '>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*'

setup(
    name='PyQUBO',
    version='0.0.1',
    author='Recruit Communications Co., Ltd.',
    description='PyQUBO allows you to create QUBOs or Ising models'
                'from mathematical expressions.',
    download_url='https://github.com/recruit-communications/pyqubo',
    license='Apache 2.0',
    packages=packages,
    install_requires=install_requires,
    include_package_data=True,
    python_requires=python_requires
)
