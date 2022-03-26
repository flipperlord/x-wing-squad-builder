"""
Setup tools
Use setuptools to install package dependencies. Instead of a requirements file you
can install directly from this file.
`pip install .`
You can install dev dependencies by targetting the appropriate key in extras_require
```
pip install .[dev] # install requires and dev requires
pip install .[docs] # install requires and docs requirements
# install requires, dev, and docs requirements all at once
pip install .[dev,docs]
```
# installing-setuptools-extras
See: https://packaging.python.org/tutorials/installing-packages/

"""
import distutils.command.build as distutils_build
import distutils.command.clean as distutils_clean
import fnmatch
import glob
import json
import os
import re
import shutil
import subprocess
import datetime
from distutils import log
from distutils.dep_util import newer
from pathlib import Path
import xml.etree.ElementTree as et

from setuptools import Command, find_packages, setup

ORGANIZATION = "ryanlenardryanlenard, Inc."
NAME = "X-Wing Squad Builder"
AUTHOR = "Will Diepholz"
AUTHOR_EMAIL = "wbdiepholz@gmail.com"
DESCRIPTION = "An interactive tool for building squads in the X-Wing miniatures game."
CONDA_ENV = "xwing"
MIN_PYTHON_VERSION = "3.8"
URL = "https://github.mmm.com/diepholz/x-wing-squad-builder"
BASE_DIR = Path(__file__).parent.absolute()
SRC_DIR = BASE_DIR / "x_wing_squad_builder"
ICON_FILE = 'icon.ico'
ICON_PATH = BASE_DIR / ICON_FILE
RESOURCES_DIR = BASE_DIR / 'qt_designer'
QRC_FILE = RESOURCES_DIR / 'resources.qrc'
ONE_FILE = True
CONSOLE = True
DEBUG = False

# Load version from module (without loading the whole module)
with open(f'{SRC_DIR}/version.py', 'r') as fd:
    VERSION = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

with open('requirements/base.txt', 'r') as f:
    REQUIRES = f.read().splitlines()

with open('requirements/dev.txt', 'r') as f:
    REQUIRES_DEV = f.read().splitlines()

with open('requirements/docs.txt', 'r') as f:
    REQUIRES_DOCS = f.read().splitlines()


class CreateCondaEnv(Command):
    """
    Requires conda.
    """

    description = "Makes a new conda environment and installs requirements via pip."

    boolean_options = []
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run_create_conda_env(self):
        env_name = CONDA_ENV
        min_version = MIN_PYTHON_VERSION
        cmd = ['conda', 'env', 'list', '--json']
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True)
        env_dict = json.loads(result.stdout)
        env_list = [Path(env_path).name for env_path in env_dict['envs']]
        if env_name not in env_list:
            cmd = ['conda', 'create', '-n',
                   f'{env_name}', f'python={min_version}', '-y']
            cmds = cmd
            cmd = ['conda', 'activate', f'{env_name}']
            cmds += ['&&'] + cmd
            cmd = ['pip', 'install', '-r', 'requirements/base.txt', '-r', 'requirements/dev.txt']
            cmds += ['&&'] + cmd
            subprocess.run(cmds, shell=True, check=True)
            log.info(f'{env_name} created successfully.')
        else:
            log.info(f'A conda environment named {env_name} already exists. A new env was not created.')

    def run(self):
        self.run_create_conda_env()


class BuildQt(Command):

    description = "Build the QT interface"

    boolean_options = []
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def make_qrc_file(self):
        def tryint(s):
            try:
                return int(s)
            except:
                return s

        def natsort_key(s):
            return [tryint(c) for c in re.split(r'(\d+)', s)]

        def find_files(top_dir, directory, patterns):
            tdir = os.path.join(top_dir, directory)
            for root, dirs, files in os.walk(tdir):
                for basename in files:
                    for pattern in patterns:
                        if fnmatch.fnmatch(basename, pattern):
                            filepath = os.path.join(root, basename)
                            filename = os.path.relpath(filepath, top_dir)
                            yield filename

        log.set_verbosity(1)
        images = [i for i in find_files(
            RESOURCES_DIR, 'images', ['*.gif', '*.png'])]
        new_images = 0
        resources = []
        if QRC_FILE.exists():
            tree = et.parse(QRC_FILE)
            root = tree.getroot()
            for resource in root.find('qresource'):
                resources.append(resource.text)
        for filename in images:
            if filename.replace('\\', '/') not in resources:
                new_images += 1
        if new_images or not QRC_FILE.exists():
            log.info(f'{new_images} images newer than {QRC_FILE} found')
            with open(QRC_FILE, 'wb+') as f:
                f.write(b'<!DOCTYPE RCC><RCC version="1.0">\n<qresource>\n')
                for filename in sorted(images, key=natsort_key):
                    f.write(('  <file>%s</file>\n' %
                             filename.replace('\\', '/')).encode())
                f.write(b'</qresource>\n</RCC>\n')
                log.info(f'File {QRC_FILE} written, {len(images)} images')

    def compile_rc_file(self):
        log.set_verbosity(1)
        py_file = os.path.join(
            SRC_DIR, "ui", f'{os.path.splitext(os.path.basename(QRC_FILE))[0]}_rc.py')
        if QRC_FILE.exists():
            if newer(QRC_FILE, py_file):
                pyrcc = 'pyside6-rcc'
                cmd = [pyrcc, str(QRC_FILE), '-o', py_file]
                status = subprocess.call(cmd, shell=False)
                if status:
                    log.warn(f'Unable to compile resource file {py_file}')
                else:
                    log.info(f'File {py_file} written')
        else:
            log.info(f'{QRC_FILE} was not found')

    def compile_ui_files(self):
        log.set_verbosity(1)
        ui_files = glob.glob(f'{RESOURCES_DIR}/*.ui')

        for ui_file in ui_files:
            py_file = os.path.join(
                SRC_DIR, "ui", f'{os.path.basename(os.path.splitext(ui_file)[0])}_ui.py')
            if not newer(ui_file, py_file):
                continue
            else:
                cmd = ['pyside6-uic',
                       ui_file, '-o', py_file, '--from-imports']
                status = subprocess.call(cmd, shell=False)
                if status:
                    log.warn(f'Unable to compile resource file {py_file}')
                else:
                    log.info(f'File {py_file} written')

    def run(self):
        self.make_qrc_file()
        self.compile_rc_file()
        self.compile_ui_files()


class CleanLocal(Command):

    description = "Clean the local project directory"

    wildcards = ['*.py[co]', '*_ui.py', '*_rc.py', '__pycache__']
    excludedirs = ['.git', 'build', 'dist']
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def _walkpaths(self, path):
        for root, dirs, files in os.walk(path):
            for excluded_dir in self.excludedirs:
                abs_excluded_dir = os.path.join(path, excluded_dir)
                if root == abs_excluded_dir or root.startswith(abs_excluded_dir + os.sep):
                    continue
            for a_dir in dirs:
                file_path = os.path.join(root, a_dir)
                if any(fnmatch.fnmatch(a_dir, pattern) for pattern in self.wildcards):
                    yield file_path
            for a_file in files:
                file_path = os.path.join(root, a_file)
                if any(fnmatch.fnmatch(file_path, pattern) for pattern in self.wildcards):
                    yield file_path

    def run(self):
        for a_path in self._walkpaths('.'):
            if os.path.isdir(a_path):
                shutil.rmtree(a_path)
            else:
                os.remove(a_path)


class BuildExe(Command):
    """
    Requires PyInstaller
    """

    description = "Generate a .exe file for distribution"

    boolean_options = []
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run_build_exe(self):
        # TODO: Make one_file a command argument like pyinstaller --onefile
        build_number = 0
        version_string = f'{VERSION}.{build_number}'
        version_list = [int(num) for num in version_string.split('.')]
        filevers = tuple(version_list)
        version_list[2] = 0
        version_list[3] = 0
        prodvers = tuple(version_list)

        version_args = {
            'publisher': ORGANIZATION,
            'display_name': NAME,
            'description': DESCRIPTION,
            'filevers': filevers,
            'prodvers': prodvers,
            'version': version_string,
            'year': str(datetime.date.today().year),
        }

        generate_file('win-version-info.txt.in', 'win-version-info.txt', version_args)

        exe_args = {
            'display_name': NAME,
            'icon_file': ICON_FILE,
            'src_dir': SRC_DIR,
            'one_file': ONE_FILE,
            'console': CONSOLE,
            'debug': DEBUG,
        }

        spec_in = os.path.join(BASE_DIR, f'{NAME}.spec.in')
        spec_out = os.path.join(BASE_DIR, f'{NAME}.spec')
        generate_file(spec_in, spec_out, exe_args)
        subprocess.call(['pyinstaller', spec_out, '--noconfirm'])
        if ONE_FILE:
            # move executable to a folder of same name for NSIS to find
            exe_dir = (BASE_DIR / 'dist' / NAME)
            exe_dir.mkdir(exist_ok=True)
            exe_file = f'{NAME}.exe'
            shutil.move(str(BASE_DIR / 'dist' / exe_file),
                        str(exe_dir / exe_file))

    def run(self):
        self.run_command("build_qt")
        self.run_build_exe()


class BuildInstaller(Command):
    """
    Requires NSIS https://nsis.sourceforge.io/Download"
    """

    description = "Generate a .exe file for windows installation"

    boolean_options = []
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run_build_installer(self):
        installer_dir = BASE_DIR / 'installer'

        # TODO implement build_number
        build_number = 0
        file_version = f'{VERSION}.{build_number}'

        installer_args = {
            'publisher': ORGANIZATION,
            'display_name': NAME,
            'description': DESCRIPTION,
            'version': VERSION,
            'icon_file': ICON_FILE,
            'icon_path': ICON_PATH,
            'base_dir': BASE_DIR,
            'file_version': file_version,
            'installer_dir': installer_dir,
        }

        nsi_in = os.path.join(installer_dir, f'{NAME}.nsi.in')
        nsi_out = os.path.join(installer_dir, f'{NAME}.nsi')
        generate_file(nsi_in, nsi_out, installer_args)

        nsis = os.path.join(
            os.environ["ProgramFiles(x86)"], "NSIS", "makensis.exe")
        subprocess.call([nsis, nsi_out])

    def run(self):
        self.run_command("build_exe")
        self.run_build_installer()


class MyBuild(distutils_build.build):
    def run(self):
        self.run_command("build_qt")
        distutils_build.build.run(self)


class MyClean(distutils_clean.clean):
    def run(self):
        self.run_command("clean_local")
        distutils_clean.clean.run(self)


def generate_file(in_filename, out_filename, variables):
    log.info('Generating %s from %s', out_filename, in_filename)
    with open(in_filename, "rt") as f_in:
        with open(out_filename, "wt") as f_out:
            f_out.write(f_in.read() % variables)


setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    url=URL,
    packages=find_packages(exclude=[
        "*.tests",
        "*.tests.*"
        "tests.*",
        "tests"
    ]),
    test_suite='tests',
    python_requires=f">={MIN_PYTHON_VERSION}",
    install_requires=REQUIRES,
    extras_require={
        'dev': REQUIRES_DEV,
        'docs': REQUIRES_DOCS,
    },
    include_package_data=True,
    keywords='application',
    zip_safe=False,
    cmdclass={
        'build': MyBuild,
        'build_qt': BuildQt,
        'build_exe': BuildExe,
        'build_installer': BuildInstaller,
        'clean': MyClean,
        'clean_local': CleanLocal,
        'create_conda_env': CreateCondaEnv,
    },
)
