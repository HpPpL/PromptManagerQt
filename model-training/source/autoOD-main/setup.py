from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="auto_od",
    version="0.1.1",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/elina-chertova/autoOD",
    classifiers=[
        "Programming Language :: Python :: 3",
        # "License :: OSI Approved :: MIT License",
        # "Operating System :: OS Independent",
    ],
    py_modules=['auto_od'],
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=requirements,
)
