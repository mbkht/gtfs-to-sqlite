from setuptools import setup, find_packages

setup(
    name='gtfs-to-sqlite',
    version='0.2.0',
    packages=find_packages('gtfs-to-sqlite'),
    include_package_data=True,
    install_requires=[
        'Click', 'pandas', 'colorama', 'numpy', 'bs4', 'requests',  'case-converter'
    ],
    entry_points={
        'console_scripts': [
            'gtfs-to-sqlite = gtfs_to_sqlite.scripts.main:cli',
        ],
    },
)
