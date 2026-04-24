"""Setup configuration for freerouter."""

from setuptools import setup, find_packages

setup(
    name="freerouter",
    version="0.1.0",
    author="Landry Simo",
    author_email="landrysimo99@gmail.com",
    description="Quota-aware LLM routing engine with automatic provider fallback",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Starland9/freerouter",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
            "isort>=5.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
