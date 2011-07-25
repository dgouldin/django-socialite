
from setuptools import setup, find_packages

setup(name='DjangoSocialite',
      packages=find_packages(),
      version=0.1,
      description="A collection of applications for playing nice with social networks.",
      author="David Gouldin",
      author_email="david@gould.in",
      url="http://gould.in",
      install_requires=[
      'Django'
      ]
      )

