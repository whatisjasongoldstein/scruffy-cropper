from distutils.core import setup
from setuptools import find_packages

setup(
    name='Scruffy Cropper',
    version="2.0.0",
    author='Jason Goldstein',
    author_email='jason@betheshoe.com',
    url='https://bitbucket.org/whatisjasongoldstein/scruffy-cropper',
    packages=find_packages(),
    include_package_data=True,
    description='Generic cropping utility for Django, plays nicely with any imagefield.',
    long_description=open('README.markdown').read(),
)