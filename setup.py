from setuptools import setup, find_packages

setup(
    name="pokemon-smile",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask",
        "pymongo",
        "requests",
        "python-dotenv",
    ],
    python_requires=">=3.11",
) 