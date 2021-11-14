from setuptools import find_packages, setup

from src.yrouter import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()


test_requires = [
    "black",
    "isort",
    "flake8",
    "pytest",
]

build_requires = [
    "twine",
    "check-wheel-contents",
]

setup(
    name="yrouter",
    version=__version__,
    description="A URL routing library.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tidiane Dia",
    author_email="tidiane.dia@therookiecoder.com",
    url="https://github.com/tijani-dia/yrouter/",
    project_urls={
        "Source": "https://github.com/tijani-dia/yrouter/",
        "Issue tracker": "https://github.com/tijani-dia/yrouter/issues/",
    },
    tests_require=test_requires,
    extras_require={
        "test": test_requires,
        "build": build_requires,
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    zip_safe=False,
    license="BSD-3-Clause",
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet :: WWW/HTTP",
    ],
)
