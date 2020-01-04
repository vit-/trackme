from setuptools import setup, find_packages

setup(
    name='trackme',
    description='TrackMe Telemetry collector',
    version='0.1.0',

    author='Vitalii Vokhmin',
    author_email='vitaliy.vokhmin@gmail.com',

    license='MIT',

    packages=find_packages(),
    install_requires=[
        'pyserial',
    ]
)
