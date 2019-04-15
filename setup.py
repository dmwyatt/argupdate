import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
        name="argupdate",
        version="0.0.1",
        author="Dustin Wyatt",
        author_email="dustin.wyatt@gmail.com",
        description="Update the value of args and kwargs destined for a callable.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/dmwyatt/argupdate",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3.7",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        python_requires='~=3.5'
)
