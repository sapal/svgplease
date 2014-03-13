from setuptools import setup

setup(
    name="svgplease",
    version="0.1",
    url="https://github.com/sapal/svgplease",
    #TODO: download_url=
    license="GPLv3",
    author="Michał Sapalski",
    author_email="sapalskimichal@gmail.com",
    description="Command line tool for manipulating svg files.",
    #TODO: long_description=
    zip_safe=True,
    classifiers=[
        #TODO: add classifiers.
    ],
    platforms="any",
    packages=["svgplease"],
    test_suite="tests.all_tests",
    #TODO: investigate if this should be True if some .svg files should be included in the package:
    include_package_data=False,
    install_requires=[]
)
