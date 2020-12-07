import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SpotiBayes-guilherme-ambrosano",
    version="0.0.6",
    author="Guilherme Ambrosano",
    author_email="guilherme.ambrosano@usp.br",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/guilherme-ambrosano/SpotiBayes",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires="==3.8",
    install_requires=["flask", "spotipy"],
)