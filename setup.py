"""Setup configuration for Astrologico."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="astrologico",
    version="1.0.0",
    author="Astrology Team",
    description="Professional astrological calculation suite for Debian/Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/astrologico",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Astronomy",
    ],
    python_requires=">=3.8",
    install_requires=[
        "skyfield>=1.54",
        "PyMeeus>=0.5.12",
        "ephem>=4.2.1",
        "astropy>=7.2.0",
        "numpy>=2.4.4",
        "scipy>=1.17.1",
    ],
    entry_points={
        "console_scripts": [
            "astrologico=cli:main",
        ],
    },
)
