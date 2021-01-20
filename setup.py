import os
import re
import sys
import platform
import subprocess
import sysconfig

from setuptools import Extension
from setuptools.command.build_ext import build_ext
from distutils.version import LooseVersion
from setuptools import Command


if os.getenv('READTHEDOCS') or platform.system() == "Linux":
    from skbuild import setup
else:
    from setuptools import setup


class PackageInfo(object):
    def __init__(self, info_file):
        with open(info_file) as f:
            exec(f.read(), self.__dict__)
        self.__dict__.pop('__builtins__', None)

    def __getattribute__(self, name):
        return super(PackageInfo, self).__getattribute__(name)

package_info = PackageInfo(os.path.join('pyqubo', 'package_info.py'))

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)', out.decode()).group(1))
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable]

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j2']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get('CXXFLAGS', ''),
                                                              self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)


class CppTest(Command):

    def initialize_options(self):
        self.cpplibdir = self.distutils_dir_name()

    def finalize_options(self):
        pass

    user_options = []

    def distutils_dir_name(self):
        """Returns the name of a distutils build directory"""
        f = "temp.{platform}-{version[0]}.{version[1]}"
        return f.format(platform=sysconfig.get_platform(),
                        version=sys.version_info)

    def run(self):
        subprocess.call(['make pyqubo_test'],
                        cwd=os.path.join('build', self.cpplibdir), shell=True)
        subprocess.call(['./tests/pyqubo_test'],
                        cwd=os.path.join('build', self.cpplibdir), shell=True)

packages = ['pyqubo', 'pyqubo.integer', 'pyqubo.utils']

install_requires = [
    'numpy<1.20,>=1.17.3',
    'dimod>=0.9.13',
    'dwave-neal>=0.5.7',
    'Deprecated>=1.2.10',
    'six>=1.11.0'
    ]


python_requires = '>=3.5, <3.10'

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
    ext_modules=[CMakeExtension('pyqubo')],
    cmdclass=dict(build_ext=CMakeBuild, cpp_test=CppTest),
    zip_safe=False,
    packages=packages,
    keywords=package_info.__keywords__,
    install_requires=install_requires,
    python_requires=python_requires,
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: Apache Software License',
    ]
)
