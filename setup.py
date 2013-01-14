from distutils.core import setup

setup(
    name='Scruffy Cropper',
    version="0.2.2",
    author='Jason Goldstein',
    author_email='jason@betheshoe.com',
    url='https://bitbucket.org/whatisjasongoldstein/django-cropper',
    packages=['cropper', 'cropper.migrations', ],
    package_data={ 'cropper': ['templates/*',] },
    description='Generic cropping utility for Django, plays nicely with any imagefield.',
    long_description=open('README.markdown').read(),
)