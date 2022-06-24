import pathlib
from setuptools import setup
from setuptools import find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="calsync",
    version="0.0.0",
    description="Python Calendar synchronizer",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/jtyers/py-calsync",
    author="Jonny Tyers",
    author_email="jonny@jonnytyers.co.uk",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[
        "google-api-python-client==2.49.0",
        "google-auth-httplib2==0.1.0",
        "google-auth-oauthlib==0.5.2",
    ],
)
