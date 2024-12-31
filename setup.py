from setuptools import setup, find_packages

setup(
    name="farmoria",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.5.0",
        "pymunk>=6.0.0",
        "pytest>=7.0.0",
    ],
    python_requires=">=3.8",
) 