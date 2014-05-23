#!/usr/bin/env python3
from setuptools import setup

setup(
    name="svgplease",
    version="0.1",
    url="https://github.com/sapal/svgplease",
    #TODO: download_url=
    license="GPLv3",
    author="Michał Sapalski",
    author_email="sapalskimichal@gmail.com",
    data_files=[
        ("", ["__main__.py"]),
        ("doc", ["../doc/grammar.txt", "../doc/change_detection_algorithm.txt"])
    ],
    description="Command line tool for manipulating svg files.",
    #TODO: long_description=
    zip_safe=True,
    classifiers=[
        #TODO: add classifiers.
    ],
    platforms="any",
    packages=["svgplease", "modgrammar"],
    test_suite="tests.all_tests",
    #TODO: investigate if this should be True if some .svg files should be included in the package:
    include_package_data=False,
    install_requires=[]
)
