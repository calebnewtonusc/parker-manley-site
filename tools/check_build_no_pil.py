"""The deploy image (python:3.12-alpine) has no Pillow. Run the build the
way it runs there, so a stray PIL import fails here and not on Railway.
2026-10-25: a PIL import in site_desk.py failed 8 deploys in a row while
the local build passed, and the live site sat on a 20:15 version."""
import runpy
import sys

sys.path.insert(0, ".")
sys.modules["PIL"] = None
sys.argv = ["build.py"]
runpy.run_path("build.py", run_name="__main__")
print("build ok without Pillow")
