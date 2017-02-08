#!/usr/bin/python
# Code taken from https://gist.github.com/didip/823887
import base64
import uuid
print(base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes))
