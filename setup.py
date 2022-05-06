import subprocess
import sys
from pathlib import Path
from shutil import rmtree

from setuptools import Command, find_packages, setup

package_name = "thu_rsvp_dataset"
here = Path(__file__).parent.resolve()
readme = (here / "README.md").read_text()


def get_version(file):
    for line in (here / file).read_text().splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


version = get_version(f"{package_name}/__init__.py")


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print(f"\033[1m{s}\033[0m")

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.status("Cleaning previous dists...")
        if (here / "dist").exists():
            rmtree(str(here / "dist"))

        self.status("Building Source and Wheel (universal) dists...")
        subprocess.run(f"{sys.executable} setup.py sdist bdist_wheel --universal", shell=True, check=True)

        self.status("Uploading the package to PyPI via Twine...")
        subprocess.run("twine upload --verbose dist/*", shell=True, check=True)

        self.status("Pushing git tags...")
        subprocess.run(f"git tag v{version}", shell=True, check=True)
        subprocess.run("git push --tags", shell=True, check=True)
        sys.exit()


with open("requirements.txt", "r") as f:
    required = f.readlines()

setup(
    name=package_name,
    version=version,
    description="Tsinghua University RSVP Benchmark Dataset",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/nik-sm/thu-rsvp-dataset.git",
    author="Niklas Smedemark-Margulies",
    author_email="niklas.sm+github@gmail.com",
    python_requires=">=3.7",
    license="MIT",
    include_package_data=True,
    packages=find_packages(),
    install_requires=required,
    cmdclass={
        "upload": UploadCommand,
    },
)
