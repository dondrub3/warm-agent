#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Warm Agent - Python包配置
"""

from setuptools import setup, find_packages
import os

# 读取README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# 读取版本号
version = {}
with open("src/__init__.py", "r", encoding="utf-8") as fh:
    exec(fh.read(), version)

setup(
    name="warm-agent",
    version=version.get("__version__", "1.0.0"),
    author="Warm Agent Team",
    author_email="contact@warm-agent.com",
    description="为AI注入温度与情感 - 让冰冷的AI回应变得温暖、有同理心",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/warm-agent/warm-agent",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
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
            "pre-commit>=3.0.0",
        ],
        "openclaw": [
            "openclaw>=0.1.0",
        ],
        "all": [
            "requests>=2.28.0",
            "pydantic>=2.0.0",
            "numpy>=1.24.0",
            "pandas>=2.0.0",
            "scikit-learn>=1.3.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "warm-agent=warm_agent.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "warm_agent": [
            "data/*.json",
            "data/*.txt",
            "configs/*.yaml",
            "configs/*.json",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/warm-agent/warm-agent/issues",
        "Source": "https://github.com/warm-agent/warm-agent",
        "Documentation": "https://docs.warm-agent.com",
        "Website": "https://warm-agent.com",
    },
    keywords=[
        "ai",
        "artificial-intelligence",
        "emotional-ai",
        "warm-ai",
        "chatbot",
        "openclaw",
        "emotional-intelligence",
        "nlp",
        "sentiment-analysis",
    ],
)