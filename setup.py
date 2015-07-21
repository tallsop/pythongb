try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'An emulator for the Nintendo Gameboy',
    'author': 'Thomas Allsop',
    'url': 'https://github.com/tallsop/pythongb',
    'version': '0.1',
    'install_requires': ['nose', 'PyOpenGL', 'PIL'],
    'packages': ['pythongb'],
    'scripts': [],
    'name': 'pythongb'
}

setup(**config)
