import os

from setuptools import setup, find_packages

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
    author_email="code-for-life-full-time-xd@ocado.com",
    description="Code for Life's common code.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ocadotechnology/codeforlife-package-python",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    data_files=[(str(DATA_DIR), data_files)],
    python_requires="==3.11.*",
    # These will be synced with Pipfile by the pipeline.
    # DO NOT edit these manually. Instead, update the Pipfile.
    install_requires=[
        "asgiref==3.6.0; python_version >= '3.7'",
        "click==8.1.3; python_version >= '3.7'",
        "django==3.2.18",
        "django-countries==7.3.1",
        "django-formtools==2.4; python_version >= '3.6'",
        "django-otp==1.1.6",
        "django-phonenumber-field==6.4.0; python_version >= '3.7'",
        "django-two-factor-auth==1.13.2",
        "djangorestframework==3.13.1",
        "flask==2.2.3",
        "importlib-metadata==6.6.0; python_version < '3.10'",
        "itsdangerous==2.1.2; python_version >= '3.7'",
        "jinja2==3.1.2; python_version >= '3.7'",
        "markupsafe==2.1.2; python_version >= '3.7'",
        "pydantic==1.10.7",
        "pypng==0.20220715.0",
        "pytz==2023.3",
        "qrcode==7.4.2; python_version >= '3.7'",
        "sqlparse==0.4.4; python_version >= '3.5'",
        "typing-extensions==4.5.0; python_version >= '3.7'",
        "werkzeug==2.2.3; python_version >= '3.7'",
        "zipp==3.15.0; python_version >= '3.7'",
    ],
    dependency_links=[],
)
