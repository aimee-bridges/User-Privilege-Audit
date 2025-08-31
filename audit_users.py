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

#Function to retrieve all local user accounts on the system
def get_local_users():
    try:
        #Run the 'net user' command to list all users
        result = subprocess.run(["net", "user"], capture_output=True, text=True)
        #Split the command output into individual lines
        lines = result.stdout.splitlines()
        #Initialize an empty list to store usernames
        users = []
        #Loop through each line of output
        for line in lines:
            #Skip lines that contain slashes or colons (not usernames)
            if "\\" in line or ":" in line:
                #Split the line into words and add to user list
                users.extend(line.strip().split())
        return users #Return the list of users
    
    except Exception as e:
        #print error message 
        print(f"Error retrieving users: {e}")
        return []
#Function to check if a given user is part of the Admin Group
def is_admin(user):
    try:
        #Run 'net user <username>' to get detailed info about user
        result = subprocess.run(["net", "user", user], capture output=True, text=True)
        #Convert the output to lowercase for easier searching
        output = result.stdout.lower()
        #check if the word 'administrators' appears in output
        return "administrators" in output
    except Exception as e:
        #Print error message
        print(f"Error checking admin status for {user}: {e}")
        return False
    