import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spotondocker", 
    version="0.1.0",
    author="Abhishek N. Kulkarni",
    author_email="abhibp1993@gmail.com",
    description="SpotOnDocker is a utility which exposes some of spot (spot.lrde.epita.fr) functionality as a dockerized service.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abhibp1993/spotondocker",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.7',
)