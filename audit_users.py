#Import required modules

#Used for interacting with OS
import os

#Allows us to run system commands and capture events
import subprocess

#Retrieves the current logged in username
import getpass

#Detects the OS type
import platform

#Function to check if the script is running on a Windows OS
def is_windows():
    #Returns True if OS is Windows
    return platform.system() == "Windows"

