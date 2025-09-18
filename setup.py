"""Setup script for arcade_dreamfactory toolkit."""

from setuptools import setup, find_packages

setup(
    name="arcade_dreamfactory",
    version="0.0.1",
    description="DreamFactory API connections toolkit for Arcade",
    author="thekevinm",
    author_email="kevin.mcgahey@dreamfactory.com",
    packages=find_packages(),
    install_requires=[
        "arcade-ai>=1.0.5",
        "arcade-tdk>=2.3.0",
        "httpx>=0.24.0",
        "loguru>=0.7.0",
    ],
    python_requires=">=3.10",
    entry_points={
        "arcade.toolkit": [
            "dreamfactory = arcade_dreamfactory.tools",
        ],
    },
)