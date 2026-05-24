"""
Configuration d'installation du package follow-up-ai
"""

from setuptools import setup, find_packages

setup(
    name="follow-up-ai",
    version="1.0.0",
    description="Pipeline de fine-tuning pour modèles LLM avec LoRA",
    author="Project NUR",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.35.0",
        "datasets>=2.14.0",
        "peft>=0.6.0",
        "trl>=0.7.0",
        "accelerate>=0.24.0",
        "bitsandbytes>=0.41.0",
        "pandas>=1.5.0",
        "openpyxl>=3.0.0",
        "pyyaml>=6.0",
        "scikit-learn>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "follow-up-ai=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
