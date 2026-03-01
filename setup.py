#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Warm Agent 安装脚本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="warm-agent",
    version="1.0.0",
    author="Dondrub3",
    author_email="dondrub3@example.com",
    description="为AI注入温度与情感的开源项目",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dondrub3/warm-agent",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "api": [
            "fastapi>=0.100.0",
            "uvicorn[standard]>=0.22.0",
            "pydantic>=2.0.0",
        ],
        "ml": [
            "numpy>=1.24.0",
            "scikit-learn>=1.3.0",
            "transformers>=4.35.0",
            "torch>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "warm-agent-api=src.api.main:main",
            "warm-agent-cli=src.cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "warm_agent": [
            "data/*.json",
            "data/*.txt",
            "models/*.pkl",
            "models/*.pt",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/dondrub3/warm-agent/issues",
        "Source": "https://github.com/dondrub3/warm-agent",
        "Documentation": "https://warm-agent.readthedocs.io/",
    },
)