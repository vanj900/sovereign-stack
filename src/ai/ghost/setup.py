"""Package configuration for thermodynamic_agency."""

from setuptools import setup, find_packages

setup(
    name="thermodynamic_agency",
    version="0.1.0",
    description="Bio-Digital Organism Architecture — thermodynamic AI agent",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.24",
        "scipy>=1.10",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
        ],
    },
)
