from setuptools import setup, find_packages

setup(
    name='trackme-traccar',
    description='TrackMe Traccar exporter',
    version='1.0.0',

    author='Vitalii Vokhmin',
    author_email='vitaliy.vokhmin@gmail.com',

    license='MIT',

    packages=find_packages(),
    install_requires=[
        'requests',
    ]
)
