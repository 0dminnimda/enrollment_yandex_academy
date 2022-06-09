import os
import re
from glob import glob

from setuptools import find_packages, setup


init = open("SBDY_app/__init__.py").read()
dunders = dict(re.findall(r"^__(\S+)__ = \"(.+)\"$", init, re.MULTILINE))

requirements = {}
for path in glob("requirements/*.txt"):
    with open(path) as file:
        name = os.path.basename(path)[:-4]
        requirements[name] = [line.strip() for line in file]

with open("README.md") as file:
    long_description = file.read()

github_link = "https://github.com/0dminnimda/enrollment_yandex_academy"

setup(
    name=dunders["name"],
    version=dunders["version"],
    description="Smol Web App that simulates online shop API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="0dminnimda",
    author_email="0dminnimda.contact@gmail.com",
    url=github_link,
    packages=find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    license="MIT",
    project_urls={
        "Bug tracker": github_link + "/issues",
    },
    install_requires=requirements.pop("basic"),
    python_requires=">=3.8",
    extras_require=requirements,
    package_data={dunders["name"]: ["py.typed"]},
)
