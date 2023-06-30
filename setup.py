#!/usr/bin/env python3
import os 

def getDeps():
    lib_folder = os.path.dirname(os.path.realpath(__file__))
    requirement_path = lib_folder + '/requirements.txt'
    os.system('pip install -r '  + requirement_path)
    # install_requires = []
    # if os.path.isfile(requirement_path):
    #     with open(requirement_path) as f:
    #         install_requires = f.read().splitlines()
    # setup(install_requires=install_requires)

getDeps()