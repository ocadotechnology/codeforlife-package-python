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
    python_requires="==3.8.*",
    # These will be synced with Pipfile by the pipeline.
    # DO NOT edit these manually. Instead, update the Pipfile.
    install_requires=[
        "asgiref==3.7.2; python_version >= '3.7'",
        "certifi==2023.7.22; python_version >= '3.6'",
        "cfl-common==6.36.2",
        "charset-normalizer==3.2.0; python_full_version >= '3.7.0'",
        "click==8.1.7; python_version >= '3.7'",
        "django==3.2.20",
        "django-cors-headers==4.1.0",
        "django-countries==7.3.1",
        "django-formtools==2.2",
        "django-otp==1.0.2",
        "django-phonenumber-field==6.4.0; python_version >= '3.7'",
        "django-two-factor-auth==1.13.2",
        "djangorestframework==3.13.1",
        "flask==2.2.3",
        "idna==3.4; python_version >= '3.5'",
        "importlib-metadata==4.13.0",
        "itsdangerous==2.1.2; python_version >= '3.7'",
        "jinja2==3.1.2; python_version >= '3.7'",
        "markupsafe==2.1.3; python_version >= '3.7'",
        "numpy==1.24.4; python_version >= '3.8'",
        "pandas==2.0.3; python_version >= '3.8'",
        "pgeocode==0.4.0; python_version >= '3.8'",
        "pydantic==1.10.7",
        "pyjwt==2.6.0; python_version >= '3.7'",
        "pypng==0.20220715.0",
        "python-dateutil==2.8.2; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "pytz==2023.3.post1",
        "qrcode==7.4.2; python_version >= '3.7'",
        "requests==2.31.0; python_version >= '3.7'",
        "six==1.16.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "sqlparse==0.4.4; python_version >= '3.5'",
        "typing-extensions==4.8.0; python_version >= '3.8'",
        "tzdata==2023.3; python_version >= '2'",
        "urllib3==2.0.4; python_version >= '3.7'",
        "werkzeug==2.3.7; python_version >= '3.8'",
        "zipp==3.17.0; python_version >= '3.8'",
    ],
    dependency_links=[],
)
