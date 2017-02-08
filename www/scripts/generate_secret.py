#!/usr/bin/python
# Code taken from https://gist.github.com/z0u/a74d6dd9a035bdd0745d
import base64
import os
print(base64.b64encode(os.urandom(50)).decode('ascii'))
