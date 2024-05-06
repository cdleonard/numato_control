from setuptools import setup

setup(
    name='numato_control',
    version='1.0.0',
    description='Wrapper for Numato USB Control Boards',
    author='Angaza',
    author_email='devices@angaza.com',
    url='http://github.com/angaza/numato_control',
    packages=['numato'],
    install_requires=[
        "pyserial>=3.0.1,<3.5",
        "enum34==1.1.6",
    ]
)
