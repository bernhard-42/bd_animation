from __future__ import print_function
from setuptools import setup, find_packages

LONG_DESCRIPTION = (
    "Build animations in OCP CAD Viewer "
    "(https://github.com/bernhard-42/vscode-ocp-cad-viewer) "
    "with build123d (https://github.com/gumyr/build123d)"
)

setup_args = {
    "name": "bd_animation",
    "version": "0.1.0",
    "description": "Build animations in OCP CAD Viewer with build123d",
    "long_description": LONG_DESCRIPTION,
    "include_package_data": True,
    "python_requires": ">=3.9",
    "install_requires": ["ocp_vscode", "build123d"],
    "extras_require": {
        "dev": {"twine", "bumpversion", "black", "pylint", "pyYaml"},
    },
    "packages": find_packages(),
    "zip_safe": False,
    "author": "Bernhard Walter",
    "author_email": "b_walter@arcor.de",
    "url": "https://github.com/bernhard-42/bd_animation",
    "keywords": ["CAD", "build123d", "OCP CAD Viewer", "animation"],
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Multimedia :: Graphics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
}

setup(**setup_args)
