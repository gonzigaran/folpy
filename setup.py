import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="folpy",
    version="0.1",
    author="Gonzalo Zigarán",
    author_email="gjzigaran@gmail.com",
    description="First Order Logic Python Library",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/gonzigaran/folpy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
