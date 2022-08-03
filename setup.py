from setuptools import setup


with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='mtg-toolbelt',
    version='0.1',
    description='A collection of tools for Magic the Gathering.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='J. Aniceto',
    license="MIT",
    packages=["mtgo_toolbelt"],
    entry_points={
        "console_scripts": [
            "mtg-tools=mtgo_toolbelt.cli"
        ]
    },
    install_requires=[],
)
