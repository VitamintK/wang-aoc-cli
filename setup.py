from setuptools import setup, find_packages

setup(
    name='wang-aoc-cli',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'aoc=aoc_cli.command_line:main'
        ]
    },
    install_requires=[
        # Any dependencies you might have
    ],
    # Additional metadata about your package
)
