"""
Setup the Code for Life package during installation. 
"""

import os

from setuptools import find_packages, setup

from codeforlife import DATA_DIR, __version__

with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()

# Walk through data directory and get relative file paths.
data_files, root_dir = [], os.path.dirname(__file__)
for dir_path, dir_names, file_names in os.walk(DATA_DIR):
    rel_data_dir = os.path.relpath(dir_path, root_dir)
    data_files += [
        os.path.join(rel_data_dir, file_name) for file_name in file_names
    ]

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
    package_data={"codeforlife": ["py.typed"]},
    python_requires="==3.8.*",
    # These will be synced with Pipfile by the pipeline.
    # DO NOT edit these manually. Instead, update the Pipfile.
    install_requires=[
        "aimmo==2.10.6",
        "asgiref==3.7.2; python_version >= '3.7'",
        "attrs==23.1.0; python_version >= '3.7'",
        "cachetools==5.3.1; python_version >= '3.7'",
        "certifi==2023.7.22; python_version >= '3.6'",
        "cfl-common==6.37.1",
        "charset-normalizer==3.3.0; python_full_version >= '3.7.0'",
        "click==8.1.7; python_version >= '3.7'",
        "codeforlife-portal==6.37.1",
        "defusedxml==0.7.1; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
        "diff-match-patch==20230430; python_version >= '3.7'",
        "django==3.2.20",
        "django-classy-tags==2.0.0",
        "django-cors-headers==4.1.0",
        "django-countries==7.3.1",
        "django-csp==3.7",
        "django-filter==23.2",
        "django-formtools==2.2",
        "django-import-export==3.3.1; python_version >= '3.8'",
        "django-js-reverse==0.9.1",
        "django-otp==1.0.2",
        "django-phonenumber-field==6.4.0; python_version >= '3.7'",
        "django-pipeline==2.0.8",
        "django-preventconcurrentlogins==0.8.2",
        "django-ratelimit==3.0.1; python_version >= '3.4'",
        "django-recaptcha==2.0.6",
        "django-sekizai==2.0.0",
        "django-treebeard==4.3.1",
        "django-two-factor-auth==1.13.2",
        "djangorestframework==3.13.1",
        "dnspython==1.16.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "et-xmlfile==1.1.0; python_version >= '3.6'",
        "eventlet==0.31.0",
        "flask==2.2.3",
        "google-auth==2.23.3; python_version >= '3.7'",
        "greenlet==3.0.0; python_version >= '3.7'",
        "hypothesis==5.41.3; python_version >= '3.6'",
        "idna==3.4; python_version >= '3.5'",
        "importlib-metadata==4.13.0",
        "itsdangerous==2.1.2; python_version >= '3.7'",
        "jinja2==3.1.2; python_version >= '3.7'",
        "kubernetes==26.1.0; python_version >= '3.6'",
        "libsass==0.22.0; python_version >= '3.6'",
        "markuppy==1.14",
        "markupsafe==2.1.3; python_version >= '3.7'",
        "more-itertools==8.7.0; python_version >= '3.5'",
        "numpy==1.24.4; python_version >= '3.8'",
        "oauthlib==3.2.2; python_version >= '3.6'",
        "odfpy==1.4.1",
        "openpyxl==3.1.2",
        "pandas==2.0.3; python_version >= '3.8'",
        "pgeocode==0.4.0; python_version >= '3.8'",
        "phonenumbers==8.12.12",
        "pillow==10.0.1; python_version >= '3.8'",
        "pyasn1==0.5.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4, 3.5'",
        "pyasn1-modules==0.3.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4, 3.5'",
        "pydantic==1.10.7",
        "pyhamcrest==2.0.2; python_version >= '3.5'",
        "pyjwt==2.6.0; python_version >= '3.7'",
        "pyotp==2.9.0",
        "pypng==0.20220715.0",
        "python-dateutil==2.8.2; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "pytz==2023.3.post1",
        "pyyaml==5.4.1; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4, 3.5'",
        "qrcode==7.4.2; python_version >= '3.7'",
        "rapid-router==5.11.3",
        "reportlab==3.6.13; python_version >= '3.7' and python_version < '4'",
        "requests==2.31.0; python_version >= '3.7'",
        "requests-oauthlib==1.3.1; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "rsa==4.9; python_version >= '3.6' and python_version < '4'",
        "setuptools==62.1.0; python_version >= '3.7'",
        "six==1.16.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "sortedcontainers==2.4.0",
        "sqlparse==0.4.4; python_version >= '3.5'",
        "tablib[html,ods,xls,xlsx,yaml]==3.5.0; python_version >= '3.8'",
        "typing-extensions==4.8.0; python_version >= '3.8'",
        "tzdata==2023.3; python_version >= '2'",
        "urllib3==2.0.6; python_version >= '3.7'",
        "websocket-client==1.6.4; python_version >= '3.8'",
        "werkzeug==3.0.0; python_version >= '3.8'",
        "xlrd==2.0.1",
        "xlwt==1.3.0",
        "zipp==3.17.0; python_version >= '3.8'",
    ],
    dependency_links=[],
)
