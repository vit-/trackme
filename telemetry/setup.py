from setuptools import setup, find_packages

setup(
    name='trackme-telemetry',
    description='TrackMe Telemetry collecting app',
    version='0.1.0',

    author='Vitalii Vokhmin',
    author_email='vitaliy.vokhmin@gmail.com',

    license='MIT',

    scripts=['bin/telemetry'],
    packages=find_packages(),
    install_requires=[
        'pyserial-asyncio',
        'pyyaml',
    ],
)
