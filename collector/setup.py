try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.md') as ptr:
    long_description = ptr.read()


setup(
    name="callspectpy",
    description="Collects execution data from python script",
    long_description=long_description,
    license="MIT",
    version="0.1.0",
    author="xliiv",
    author_email="tymoteusz.jankowski@gmail.com",
    maintainer="xliiv",
    maintainer_email="tymoteusz.jankowski@gmail.com",
    url="https://github.com/xliiv/callspect",
    packages=['callspectpy'],
    entry_points={
        'console_scripts': [
            'callspectpy = callspectpy_cli:run',
        ],
    },
    classifiers=[
      'Programming Language :: Python :: 3',
    ]
)
