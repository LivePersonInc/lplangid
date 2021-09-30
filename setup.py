import glob
from setuptools import setup

setup(
    name='lplangid',  # Required.
    version='0.1.2',  # Required. Use major.minor.dev format.
    description='LivePerson language detection package using a Reciprocal Rank Classifier',  # Required
    long_description='This package is a python implementation of the classifier described in the paper '
                     'Language Identification with a Reciprocal Rank Classifier".',
    long_description_content_type='text/x-rst',

    packages=['lplangid', 'training'],
    include_package_data=True,
    data_files=[('lplangid/freq_data', glob.glob('lplangid/freq_data/*.csv'))],

    # No new packages are needed for running lplangid - the below are useful for development.
    # install_requires=['flake', 'pytest'],  # List new package requirements here, but please be sure you need them!

    url='https://github.com/LivePersonInc/lplangid',  # Optional
    author='Dominic Widdows, Chris Brew',  # Optional
    author_email='dwiddows@gmail.com,christopher.brew@gmail.com',  # Optional
    keywords='language detection, language classification, reciprocal rank classifier, lplangid'
)
