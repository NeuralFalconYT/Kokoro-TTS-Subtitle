import platform
import os

bat_content = """@echo off
call myenv\\Scripts\\activate
@python.exe beta.py %*
@pause
"""

sh_content = """#!/bin/bash
source myenv/bin/activate
python3 beta.py "$@"
"""

if platform.system() == "Windows":
    with open("run_app.bat", "w") as file:
        file.write(bat_content)
    print("run_app.bat file created successfully!")
else:
    with open("run_app.sh", "w") as file:
        file.write(sh_content)
    os.chmod("run_app.sh", 0o755)
    print("run_app.sh file created successfully and made executable!")
