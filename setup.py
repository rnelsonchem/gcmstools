from setuptools import setup, find_packages

setup(
    name = "gcmstools",
    version = "0.1.0",

    description = "Tools for working with GCMS files.",
    url = "https://github.com/rnelsonchem/gcms_nnls",

    author = "Ryan Nelson",
    author_email = "rnelsonchem@gmail.com",

    license = "MIT",

    keywords = "gcms aia nnls",

    packages = find_packages(),
    install_requires = [
        'numpy>=1.9.1',
        'matplotlib>=1.4.2',
        'netCDF4>=1.0.4',
        'tables>=3.1.1',
        'scipy>=0.14.0',
    ],

    package_data = {
        'gcmstools': [
            'sampledata/*',
        ],
    },
)

