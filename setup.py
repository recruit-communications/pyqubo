import os
import re
import sys
import platform
import subprocess
import sysconfig

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from distutils.version import LooseVersion
from setuptools import Command



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
    'numpy>=1.16.0,<2.0.0',
    'dimod>=0.9.2',
    'dwave-neal>=0.5.4'
    ]


setup(
    name='pyqubo',
    version='1.0.7',
    author='Recruit Communications Co.,Ltd.',
    author_email='',
    description='PyQUBO',
    long_description='',
    ext_modules=[CMakeExtension('pyqubo')],
    cmdclass=dict(build_ext=CMakeBuild, cpp_test=CppTest),
    zip_safe=False,
    packages=packages,
    install_requires=install_requires
)
