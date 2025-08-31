#Import required modules

# Import descriptions from external file
from privileges import PRIVILEGE_DESCRIPTIONS

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
        # Run 'net user' to list all local users
        result = subprocess.run(["net", "user"], capture_output=True, text=True)
        lines = result.stdout.splitlines()

        users = []
        capture = False

        for line in lines:
            # Start capturing usernames after this header line
            if "User accounts for" in line:
                capture = True
                continue

            # Stop capturing when we hit the command summary
            if capture and ("The command completed successfully" in line or line.strip() == ""):
                break

            # If we're in the capture zone, extract usernames
            if capture:
                users.extend(line.strip().split())

        return users

    except Exception as e:
        print(f"❌ Error retrieving users: {e}")
        return []
#Function to check if a given user is part of the Admin Group
def is_admin(user):
    try:
        #Run 'net user <username>' to get detailed info about user
        result = subprocess.run(["net", "user", user], capture_output=True, text=True)
        #Convert the output to lowercase for easier searching
        output = result.stdout.lower()
        #check if the word 'administrators' appears in output
        return "administrators" in output
    except Exception as e:
        #Print error message
        print(f"Error checking admin status for {user}: {e}")
        return False
#Main function that runs the audit
def main():
    #Check if OS = Windows

    if not is_windows():
        print("This scirpt currently supports Windows only.")
        return
    
    print("User Privilege Audit Tool\n")
    #get the current logged in user
    current_user = getpass.getuser()
    print(f"Current user: {current_user}\n")
    #Retrieve all local users
    users = get_local_users()
    #Loop through each user and check their privilege level
    for user in users:
         #Determine if the user is an admin 
         admin_status = is_admin(user)
         #Choose a label based on their privilege level
         status ="Administrator" if admin_status else "Standard User"
         #Print the result for each user
         print(f" - {user}: {status}")
#Run main function only if script is executed directly
if __name__ == "__main__":
     main()