from setuptools import setup, find_packages

with open('README.rst') as file:
    long_description = file.read()

setup(
    name = "gcmstools",
    version = "0.1.1",

    description = "Tools for working with GCMS files.",
    long_description = long_description,
    url = "https://github.com/rnelsonchem/gcmstools",

    author = "Ryan Nelson",
    author_email = "rnelsonchem@gmail.com",

    license = "BSD",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords = "gcms aia nnls",

    packages = find_packages(),
    install_requires = [
        'numpy>=1.9.1',
        'matplotlib>=1.4.2',
        'tables>=3.1.1',
        'scipy>=0.14.0',
        'pandas>=0.15.2',
        'IPython>=2.3.1',
    ],

    package_data = {
        'gcmstools': [
            'sampledata/*',
        ],
    },
)

