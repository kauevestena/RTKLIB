try:
    from scripts.lib import *
except ImportError:
    from lib import *

import shutil

# if lib is imported, python modules are installed correctly
print("Libraries installed successfully") 

# now test the symlinks:
if os.path.exists(rootpath_data):
    print(f"rootpath_data exists: {os.listdir(rootpath_data)}")

# check if "xterm" is installed
if shutil.which("xterm"):
    print("xterm is installed")