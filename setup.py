from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name="tinydebug", version="0.1.1", packages=["tinydebug", "tinydebug.TestSuite"], entry_points={"console_scripts": ["tinydebug = tinydebug.tinydebug:main"]},
      author="Maya Farber Brodsky", author_email="mayaf2003@gmail.com", description="Python Debugger that creates shareable video logs of a program's execution.",
      long_description=long_description, long_description_content_type="text/markdown", url="https://github.com/CCExtractor/AZTinyDebug",
      download_url="https://github.com/CCExtractor/AZTinyDebug/tarball/0.1.1", license="MIT", include_package_data=True,
      install_requires=['Pillow', 'opencv-python', 'numpy', 'pyyaml'], classifiers=["Programming Language :: Python :: 3", "License :: OSI Approved :: MIT License"])
