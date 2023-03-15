from setuptools import setup, find_packages
import os

from codeforlife import DATA_DIR, __version__


with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()

# Walk through data directory and get relative file paths.
data_files, root_dir = [], os.path.dirname(__file__)
for dir_path, dir_names, file_names in os.walk(DATA_DIR):
    rel_data_dir = os.path.relpath(dir_path, root_dir)
    data_files += [os.path.join(rel_data_dir, file_name) for file_name in file_names]

setup(
    name="codeforlife",
    version=__version__,
    author="Ocado",
    author_email="codeforlife@ocado.com",
    description="Code for Life's common code.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ocadotechnology/codeforlife-package-python",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[],
    dependency_links=[],
    include_package_data=True,
    data_files=[(str(DATA_DIR), data_files)],
    python_requires="==3.7.*",
)
