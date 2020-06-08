from os import path
from setuptools import setup, find_packages

# the bedmap2 version
__version__ = "0.0.1"

# get the absolute path of this project
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# the standard setup info
setup(
    name="bedmap2",
    version=__version__,
    description="A Python interface to the Antarctic BEDMAP2 model. ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rprechelt/bedmap2",
    author="Remy L. Prechelt",
    author_email="prechelt@hawaii.edu",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords=["antarctica dem bedmap2 ice"],
    packages=["bedmap2"],
    python_requires=">=3.6*, <4",
    install_requires=[],
    extras_require={
        "test": ["pytest", "black", "mypy",
                 "coverage", "pytest-cov", "flake8"],
    },
    scripts=[],
    project_urls={},
    include_package_data=True,
)
