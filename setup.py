from setuptools import setup, find_packages

setup(
    name='gtfs-to-sqlite',
    version='0.2.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click', 'pandas', 'numpy', 'bs4', 'requests', 'case-converter','tqdm'
    ],
    entry_points={
        'console_scripts': [
            'gtfstosqlite = gtfstosqlite.scripts.gtfstosqlite:cli',
        ],
    },
)
