from distutils.core import setup

setup(
    name='Django Cropper',
    version="0.1",
    author='Jason Goldstein',
    author_email='jason@betheshoe.com',
    url='https://bitbucket.org/whatisjasongoldstein/django-cropper',
    packages=['cropper', 'cropper.migrations', ],
    description='Generic cropping utility, plays nicely with any Django imagefield.',
    long_description=open('README.markdown').read(),
)