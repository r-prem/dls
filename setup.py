from setuptools import find_packages, setup

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in dls/__init__.py
from dls import __version__ as version

setup(
	name="dls",
	version=version,
	description="Digital Learning Management System",
	author="Raffael",
	author_email="raffaelprem@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires,
)
