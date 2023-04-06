from setuptools import setup

setup(
    name="e-waste-blockchain",
    version="0.1",
    install_requires=[
        "protobuf==3.20.1",
        "abci==0.8.3",
        "sqlitedict==2.1.0",
        "ecdsa==0.18.0",
        "grequests==0.6.0",
    ],
)
