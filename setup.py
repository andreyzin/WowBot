import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="WowBot", # Replace with your own username
    version="2.1.1",
    author="Andrey",
    author_email="zinovand@gmail.com",
    description="Powerful bots utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andeyzin/wowbot",
    packages=setuptools.find_packages(),
    license='GPL3',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)