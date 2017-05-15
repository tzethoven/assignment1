import sys
from cx_Freeze import setup, Executable

include_files = ["autorun.inf"]
base = None

if sys.platform == "win32":
    base = "Win32GUI"

setup(name="CIM Parser",
      version="9000",
      description="Parses CIM",
      options={"build_exe": {"include_files": include_files}},
      executables=[Executable("assignment1_final.py", base=base)])