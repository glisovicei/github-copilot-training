from setuptools import setup, find_packages
from pathlib import Path

# Read README with explicit UTF-8 encoding for Windows compatibility
readme_path = Path(__file__).parent / "README.md"
try:
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
except Exception:
    long_description = "Airline Discount ML Training Repository"

setup(
    name='airline_discount_ml',
    version='0.1.0',
    author='Airline ML Team',
    author_email='team@airline-ml.com',
    description='A training project for learning GitHub Copilot with ML - generates customized airline discounts',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'numpy>=1.20.0',
        'pandas>=1.3.0',
        'scikit-learn>=1.0.0',
        'sqlalchemy>=2.0.0',
        'matplotlib>=3.5.0',
        'seaborn>=0.11.0',
        'flask>=3.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'jupyter>=1.0.0',
            'jupyterlab>=4.0.0',
            'ipykernel>=6.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'fastapi>=0.110.0',
            'uvicorn[standard]>=0.23.0',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)