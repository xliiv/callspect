try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.md') as ptr:
    long_description = ptr.read()


setup(
    name="callspect",
    description="Inspect program execution from data generated by `callspectpy`",
    long_description=long_description,
    license="MIT",
    version="0.1.3",
    author="xliiv",
    author_email="tymoteusz.jankowski@gmail.com",
    maintainer="xliiv",
    maintainer_email="tymoteusz.jankowski@gmail.com",
    url="https://github.com/xliiv/callspect",
    python_requires='>=3.5',
    install_requires=[
        'Flask==1.0',
    ],
    packages=['callspect'],
    py_modules=['callspect_cli'],
    entry_points={
        'console_scripts': [
            'callspect = callspect_cli:run',
        ],
    },
    include_package_data=True,
    classifiers=[
      'Programming Language :: Python :: 3',
    ]
)
