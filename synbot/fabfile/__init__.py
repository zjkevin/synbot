#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

import os, re
mds = [re.match(r'^([a-zA-Z].*)\.py$', md) for md in os.listdir(os.path.dirname(__file__))]
mds = [md.groups()[0] for md in mds if md]
for md in mds:__import__(__name__+'.'+ md)