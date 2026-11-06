#!/usr/bin/env python3
"""The site has to build on a bare Mac, whose /usr/bin/python3 is 3.9.

On 2026-11-06 build.py only compiled on Python 3.12+, so "run it on my laptop"
would have failed on Parker's first day owning the site. Run this with the
system Python: /usr/bin/python3 tools/check_system_python.py
"""
import sys

for name in ("build.py", "site_desk.py"):
    compile(open(name, encoding="utf-8").read(), name, "exec")
print("ok: both compile on Python", sys.version.split()[0])
