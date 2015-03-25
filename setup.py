import os
from setuptools import setup

setup(
    name = "travelling_salesman",
    version = "0.0.1",
    author = "Bartlomiej Marcinowski",
    author_email = "s1040301@sms.ed.ac.uk",
    description = ("Implementation of a Travelling Salesman Problem solver"
                   "using an Ant Colony Optimization algorithm."),
    license = "MIT",
    keywords = "travelling salesman ant colony optimization",
    packages=['travelling_salesman'],
    classifiers=[
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)
