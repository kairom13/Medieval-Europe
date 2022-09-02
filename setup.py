"""
A simple setup script to create an executable using PyQt5. This also
demonstrates the method for creating a Windows executable that does not have
an associated console.
PyQt5app.py is a very simple type of PyQt5 application
Run the build process by running the command 'python setup.py build'
If everything works well you should find a subdirectory in the build
subdirectory that contains the files needed to run the application
"""

from cx_Freeze import Executable, setup

## For Mac: python ./setup.py bdist_mac
## For Windows: python ./setup.py bdist_msi

try:
    from cx_Freeze.hooks import get_qt_plugins_paths
except ImportError:
    include_files = []
else:
    include_files = get_qt_plugins_paths("PyQt5", "platforms")

name = 'Medieval European Database'

build_exe_options = {
    "excludes": ["tkinter"],
    "include_files": include_files,
    "zip_include_packages": ["PyQt5"],
}

bdist_mac_options = {
    "bundle_name": name,
    "iconfile": 'Medieval_European_Database_icon.png'
}

bdist_dmg_options = {
    "volume_label": name,
}


executables = [Executable("Medieval_Europe/Code/main.py", base=None, target_name=name)]

setup(
    name=name,
    version="0.1",
    description="Sample cx_Freeze PyQt5 script",
    options={
        #"build_exe": build_exe_options,
        "bdist_mac": bdist_mac_options
    },
    executables=executables,
)