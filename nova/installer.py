import os
import shutil
import time
import urllib.request
from urllib.request import urlretrieve
import subprocess
import sys

# Function to ensure required libraries are installed
def install_required_libraries():
    required_libraries = ["pywin32"]

    for lib in required_libraries:
        try:
            # Try to import the library
            __import__(lib)
        except ImportError:
            # If library is not installed, install it using pip
            print(f"Installing {lib}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

def create_folders_and_files():
    # Define the target directory for the app installation
    user_documents = os.path.expanduser("~\\Documents")
    nova_app_folder = os.path.join(user_documents, "NovaApp")
    assets_folder = os.path.join(nova_app_folder, "assets")

    # Create necessary directories if they don't exist
    if not os.path.exists(nova_app_folder):
        os.makedirs(nova_app_folder)
    if not os.path.exists(assets_folder):
        os.makedirs(assets_folder)

    # Download the icon and save it in the assets folder
    icon_url = "https://raw.githubusercontent.com/3rik11/nova/main/icon.ico"
    icon_path = os.path.join(assets_folder, "icon.ico")
    download_icon(icon_url, icon_path)

    # Define the URL for app.py
    app_url = "https://raw.githubusercontent.com/3rik11/nova/main/app.py"
    app_file_path = os.path.join(nova_app_folder, "app.py")

    # Download app.py content from the URL and save to the file
    download_file(app_url, app_file_path)

    print(f"App installed at {app_file_path}")

    # Create a Windows shortcut on Desktop to run app.py
    create_shortcut_on_desktop(app_file_path, icon_path)

    # Download and install the uninstaller script
    uninstaller_url = "https://raw.githubusercontent.com/3rik11/nova/main/uninstaller.py"
    uninstaller_file_path = os.path.join(nova_app_folder, "uninstaller.py")
    download_file(uninstaller_url, uninstaller_file_path)
    print(f"Uninstaller installed at {uninstaller_file_path}")

def download_icon(url, path):
    """Download the icon from the given URL and save it to the specified path"""
    try:
        urlretrieve(url, path)
        print(f"Icon downloaded to {path}")
    except Exception as e:
        print(f"Failed to download icon: {e}")

def download_file(url, path):
    """Download a file from a URL and save it to the specified path"""
    try:
        urllib.request.urlretrieve(url, path)
        print(f"File downloaded from {url} to {path}")
    except Exception as e:
        print(f"Failed to download file: {e}")

def create_shortcut_on_desktop(app_file_path, icon_path):
    # Define the shortcut path
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    shortcut_path = os.path.join(desktop_path, "NOVA Assistant.lnk")

    # Define the command to run the app.py (in CMD) and set the icon for the CMD window
    target = "cmd.exe"
    arguments = f"/K python \"{app_file_path}\""  # Run app.py using cmd
    icon = icon_path  # Use the downloaded icon for the shortcut and CMD window

    # Create a Windows shortcut (.lnk) using the pywin32 library
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = target
        shortcut.Arguments = arguments
        shortcut.IconLocation = icon
        shortcut.save()
        print(f"Shortcut created at {shortcut_path}")
    except ImportError:
        print("Error creating shortcut. Please install pywin32 using 'pip install pywin32'")

if __name__ == "__main__":
    # Ensure required libraries are installed
    install_required_libraries()

    # Proceed with the installation of folders and files
    create_folders_and_files()
