import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.md')) as f:
    CHANGES = f.read()

requires = [
    'paho-mqtt',
    'smbus2'
]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest >= 3.7.4',
    'pytest-cov',
]

setup(
    name='synergy-monitor',
    version='0.0',
    description='Synergy Monitor',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Programming Language :: Python',
    ],
    author='Pearce Ropion & Sarah Johnson',
    author_email='pearce.ropion@me.com',
    url='',
    keywords='energy monitor mqtt',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
    },
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = synergy:main',
        ],
    },
)
