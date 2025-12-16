"""Setup configuration for Bongo Cat desktop application."""

from setuptools import setup, find_packages
import os

# Read the long description from README
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

setup(
    name="bongo-cat",
    version="2.0.0",
    author="luinbytes",
    description="Interactive desktop pet that responds to keyboard, mouse, and controller inputs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luinbytes/bongocat",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt5>=5.15.10",
        "pygame>=2.6.0",
        "pynput>=1.7.6",
        "pywin32>=306; platform_system=='Windows'",
    ],
    extras_require={
        "dev": [
            "pyinstaller>=5.0",
            "pytest>=7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "bongo-cat=bongo_cat.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.png", "*.json", "*.wav", "*.ini"],
    },
)
