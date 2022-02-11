import io
import re
import os
import subprocess
from pkg_resources import parse_requirements
from setuptools import find_packages, setup, Command
from setuptools.command.bdist_egg import bdist_egg as _bdist_egg
from setuptools.command.develop import develop as _develop
from distutils.command.build import build as _build
import shutil

SETUP_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS = ["guacamol", "matplotlib", "torch", "joblib", "numpy", "tqdm", "cython", "nltk"]


class fetch_guacamol_datasets(Command):
    """
    Run installation to fetch guacamol datasets.
    """

    def initialize_options(self):
        """Set initialize options."""
        pass

    def finalize_options(self):
        """Set finalize options."""
        pass

    def run(self):
        """Run installation to fetch guacamol datasets."""
        try:
            build_directory = os.path.join(SETUP_DIR, "build_", "data")
            package_directory = os.path.join(SETUP_DIR, "guacamol_baselines", "data")
            os.makedirs(package_directory, exist_ok=True)
            os.makedirs(build_directory, exist_ok=True)
            subprocess.check_call(
                [os.path.join(SETUP_DIR, "fetch_guacamol_dataset.sh"), build_directory]
            )
            guacamol_built_files = [
                os.path.join(build_directory, entry)
                for entry in os.listdir(build_directory)
                if (entry.startswith("guacamol") and entry.endswith(".smiles"))
            ]

            for module_file in guacamol_built_files:
                shutil.copy(module_file, package_directory)
            try:
                if self.develop:
                    pass
                else:
                    raise AttributeError
            except AttributeError:
                print("Cleaning up")
                shutil.rmtree(build_directory, ignore_errors=True)
        except subprocess.CalledProcessError as error:
            raise EnvironmentError(
                f"Failed to fetch of guacamol datasets dependencies via {error.cmd}."
            )


class build(_build):
    """Build command."""

    sub_commands = [("fetch_guacamol_datasets", None)] + _build.sub_commands


class bdist_egg(_bdist_egg):
    """Build bdist_egg."""

    def run(self):
        """Run build bdist_egg."""
        self.run_command("fetch_guacamol_datasets")
        _bdist_egg.run(self)


class develop(_develop):
    """Build develop."""

    def run(self):
        """Run build develop."""
        setup_guacamol_datasets = self.distribution.get_command_obj(
            "fetch_guacamol_datasets"
        )
        setup_guacamol_datasets.develop = True
        self.run_command("fetch_guacamol_datasets")
        _develop.run(self)


# ease installation during development
vcs = re.compile(r"(git|svn|hg|bzr)\+")
try:
    with open("dockers/requirements.txt") as fp:
        REQUIREMENTS.extend([
            str(requirement)
            for requirement in parse_requirements(fp)
            if vcs.search(str(requirement))
        ])
except FileNotFoundError:
    # requires verbose flags
    print("requirements.txt not found.")

match = re.search(
    r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
    io.open("guacamol_baselines/__init__.py", encoding="utf_8_sig").read(),
)
if match is None:
    raise SystemExit("Version number not found.")
__version__ = match.group(1)

setup(
    name="guacamol_baselines",
    version=__version__,
    author="GT4SD Team",
    description="Baseline model implementations for guacamol benchmark adapted for GT4SD",
    packages=find_packages(),
    package_dir={"guacamol_baselines": "guacamol_baselines"},
    package_data={"guacamol_baselines": ["data/guacamol*.smiles", "smiles_lstm_hc/pretrained_model/model*.json", "smiles_lstm_hc/pretrained_model/model*.pt", "graph_mcts/*.p", "smiles_lstm_ppo/pretrained_model/model*.json", "smiles_lstm_ppo/pretrained_model/model*.pt"]},
    long_description=open("README.md").read(),
    url="https://github.com/GT4SD/guacamol_baselines.git",
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    cmdclass={
        "bdist_egg": bdist_egg,
        "build": build,
        "fetch_guacamol_datasets": fetch_guacamol_datasets,
        "develop": develop,
    },
    install_requires=REQUIREMENTS,
)
