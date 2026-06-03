#!/usr/bin/env python3
"""
Setup script for MP3 Cover Art Manager
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="mp3-cover-art-manager",
    version="1.0.0",
    author="Washington Indacochea Delgado",
    author_email="linuxfrontier@proton.me",
    description="A graphical application to search and add album art to MP3 files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mp3-cover-art-manager",
    license="GPL-3.0",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Audio",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
    ],
    python_requires=">=3.9",
    install_requires=[
        "PyQt6>=6.0.0",
        "requests>=2.25.0",
        "mutagen>=1.45.0",
    ],
    entry_points={
        "console_scripts": [
            "mp3-cover-art-manager=cover_finder:main",
        ],
    },
    include_package_data=True,
    data_files=[
        ("share/pixmaps", ["cover_finder.svg"]),
        ("share/mp3-cover-art-manager/translations", ["translations/cover_art_en.qm", "translations/cover_art_es.qm"]),
        ("share/doc/mp3-cover-art-manager", ["README.md", "LICENSE", "TRANSLATIONS.md"]),
    ],
)
