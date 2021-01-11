from setuptools import setup, find_packages

with open("README.md", "r") as fh:
  long_description = fh.read()

with open("requirements.txt") as fh:
  install_requires = fh.read()

setup(
  name="phxsocket",
  version="0.1.0",
  author="wwwwwwww",
  author_email="wvvwvvvvwvvw@gmail.com",
  description="Websocket client for Phoenix Elixir",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/wwww-wwww/phxsocket",
  install_requires=install_requires,
  packages=find_packages(),
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: OS Independent",
  ],
  python_requires=">=3.6",
)
