#!/usr/bin/env python3
from setuptools import setup

setup(
    name="svgplease",
    version="0.2",
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
    long_description=("svgplease is a command line tool for manipulating svg images. " +
                      "The commands can be specified in simple language very similar to standard " +
                      "English syntax."),
    zip_safe=True,
    classifiers=[
        "Topic :: Multimedia :: Graphics",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Environment :: Console",
        "Development Status :: 2 - Pre-Alpha",
    ],
    platforms="any",
    packages=["svgplease", "modgrammar"],
    test_suite="tests.all_tests",
    include_package_data=False,
    install_requires=[]
)
