import os
import platform
import re
import subprocess
import sys
import sysconfig
from distutils.version import LooseVersion
from importlib.util import find_spec

from setuptools import setup, Command, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.test import test as TestCommand

# Convert distutils Windows platform specifiers to CMake -A arguments
PLAT_TO_CMAKE = {
    "win32": "Win32",
    "win-amd64": "x64",
    "win-arm32": "ARM",
    "win-arm64": "ARM64",
}

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
            if cmake_version < '3.17':
                raise RuntimeError("CMake >= 3.17 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        # required for auto-detection of auxiliary "native" libs
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep

        cfg = 'Debug' if self.debug else 'Release'
        cmake_generator = os.environ.get("CMAKE_GENERATOR", "")
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable, 
                      "-DCMAKE_BUILD_TYPE={}".format(cfg),  # not used on MSVC, but no harm
                     ]
        build_args = []
        
        if platform.system() != "Windows":
            # Using Ninja-build since it a) is available as a wheel and b)
            # multithreads automatically. MSVC would require all variables be
            # exported for Ninja to pick it up, which is a little tricky to do.
            # Users can override the generator with CMAKE_GENERATOR in CMake
            # 3.15+.
            if not cmake_generator:
                try:
                    import ninja  # noqa: F401

                    cmake_args += ["-GNinja"]
                except ImportError:
                    pass

        else:

            # Single config generators are handled "normally"
            single_config = any(x in cmake_generator for x in {"NMake", "Ninja"})

            # CMake allows an arch-in-generator style for backward compatibility
            contains_arch = any(x in cmake_generator for x in {"ARM", "Win64"})

            # Specify the arch if using MSVC generator, but only if it doesn't
            # contain a backward-compatibility arch spec already in the
            # generator name.
            if not single_config and not contains_arch:
                cmake_args += ["-A", PLAT_TO_CMAKE[self.plat_name]]

            # Multi-config generators have a different way to specify configs
            if not single_config:
                cmake_args += [
                    "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}".format(cfg.upper(), extdir)
                ]
                build_args += ["--config", cfg]
        
        # disable macos openmp since addtional dependency is needed.
        if platform.system() == 'Darwin':
            # Cross-compile support for macOS - respect ARCHFLAGS if set
            archs = re.findall(r"-arch (\S+)", os.environ.get("ARCHFLAGS", ""))
            if archs:
                cmake_args += ["-DCMAKE_OSX_ARCHITECTURES={}".format(";".join(archs))]
        # Set CMAKE_BUILD_PARALLEL_LEVEL to control the parallel build level
        # across all generators.
        if "CMAKE_BUILD_PARALLEL_LEVEL" not in os.environ:
            # self.parallel is a Python 3 only way to set parallel jobs by hand
            # using -j in the build_ext call, not supported by pip or PyPA-build.
            if hasattr(self, "parallel") and self.parallel:
                # CMake 3.12+ only.
                build_args += ["-j{}".format(self.parallel)]       
        if "USE_TEST" in os.environ:  
            cmake_args += ["-DUSE_TEST=Yes", "-LA", "-LH"]      
            
        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get('CXXFLAGS', ''), self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)


class GoogleTestCommand(TestCommand):
    """
    A custom test runner to execute both Python unittest tests and C++ Google Tests.
    """

    def distutils_dir_name(self, dname):
        """Returns the name of a distutils build directory"""
        dir_name = "{dirname}.{platform}-{version[0]}.{version[1]}"
        return dir_name.format(dirname=dname,
                               platform=sysconfig.get_platform(),
                               version=sys.version_info)

    def run(self):
        # Run Python tests
        super(GoogleTestCommand, self).run()
        print("\nPython tests complete, now running C++ tests...\n")
        # Run catch tests
        print(os.path.join('build/', self.distutils_dir_name('lib')))
        subprocess.call(['make pyqubo_test'],
                        cwd=os.path.join('build',
                                         self.distutils_dir_name('temp')),
                        shell=True)
        subprocess.call(['./tests/pyqubo_test'],
                        cwd=os.path.join('build',
                                         self.distutils_dir_name('temp')),
                        shell=True)


class PyTestCommand(TestCommand):
    def run(self):
        super().run()


packages = ['pyqubo', 'pyqubo.integer', 'pyqubo.utils']

install_requires = [
        'numpy>=1.17.3',
        "dimod>=0.10.0, <0.11",
        'dwave-neal>=0.5.7',
        'Deprecated>=1.2.12',
        'six>=1.15.0'
        ]


tests_require = [
        'coverage>=4.5.1',
        'codecov>=2.1.9'
        ]

python_requires = '>=3.7, <=3.10'

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
        ext_modules=[CMakeExtension('cpp_pyqubo')],
        cmdclass=dict(build_ext=CMakeBuild, test=GoogleTestCommand, pytest=PyTestCommand),
        zip_safe=False,
        packages=packages,
        keywords=package_info.__keywords__,
        install_requires=install_requires,
        python_requires=python_requires,
        tests_require=tests_require,
        include_package_data=True,
        classifiers=[
                'Programming Language :: Python :: 3.7',
                'Programming Language :: Python :: 3.8',
                'Programming Language :: Python :: 3.9',
                'Programming Language :: Python :: 3.10',
                'License :: OSI Approved :: Apache Software License',
                'Operating System :: MacOS :: MacOS X',
                'Operating System :: Microsoft :: Windows :: Windows 10', 
                'Operating System :: POSIX :: Linux',
                ]
        )
