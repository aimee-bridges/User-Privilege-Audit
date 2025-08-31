# Dictionary mapping privilege labels to descriptions
PRIVILEGE_DESCRIPTIONS = {
    "Administrator": "Full system access: can install software, manage users, and change settings.",
    "Standard User": "Limited access: can run applications and change personal settings, but not system-wide configurations.",
    "Guest": "Minimal access: temporary use with very restricted permissions."
}
# Import standard Python modules
import os                     # For interacting with the operating system
import subprocess             # To run system commands and capture their output
import getpass                # To get the current logged-in username
import platform               # To detect the operating system type
import win32com.client        # For Windows COM interactions

# Import the privilege descriptions from the external file
from privileges import PRIVILEGE_DESCRIPTIONS

# Function to check if the script is running on a Windows system
def is_windows():
    return platform.system() == "Windows"  # Returns True if OS is Windows

# Function to retrieve all local user accounts using the 'net user' command
def get_local_users():
    try:
        # Run 'net user' and capture the output
        result = subprocess.run(["net", "user"], capture_output=True, text=True)
        lines = result.stdout.splitlines()  # Split output into lines

        users = []       # List to store usernames
        capture = False  # Flag to start capturing usernames

        for line in lines:
            # Start capturing after this header line
            if "User accounts for" in line:
                capture = True
                continue

            # Stop capturing when we reach the end of the user list
            if capture and ("The command completed successfully" in line or line.strip() == ""):
                break

            # If we're in the capture zone, extract usernames from the line
            if capture:
                users.extend(line.strip().split())

        return users  # Return the list of usernames

    except Exception as e:
        # Print an error message if something goes wrong
        print(f"Error retrieving users: {e}")
        return []
#Function to get last login time for specific user
def get_last_login(user):
    try:
        locator = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        services = locator.ConnectServer(".", "root\\cimv2")
        query = f"SELECT * FROM Win32_NetworkLoginProfile WHERE Name = '{user}'"
        results = services.ExecQuery(query)

        for item in results:
            if item.LastLogon:
                # Returns raw timestamp string
                return item.LastLogon
        return "Not available"
    except Exception as e:
        return f"Error retrieving login time: {e}"

# Function to check if a user is part of the Administrators group
def is_admin(user):
    try:
        # Run 'net user <username>' to get detailed info
        result = subprocess.run(["net", "user", user], capture_output=True, text=True)
        output = result.stdout.lower()  # Convert output to lowercase for easier matching

        # Check if the word 'administrators' appears in the output
        return "administrators" in output

    except Exception as e:
        # Print an error message if something goes wrong
        print(f"Error checking admin status for {user}: {e}")
        return False

# Main function that runs the audit
def main():
    # Detect the operating system type
    os_type = platform.system()

    # Display tool header
    print("User Privilege Audit Tool\n")

    # Show the operating system
    print(f"Operating System: {os_type}")

    # Get and display the current logged-in user
    current_user = getpass.getuser()
    print(f"Current User: {current_user}\n")

    # If not running on Windows, exit early
    if not is_windows():
        print("This script currently supports Windows only.\n")
        return

    # Show the OS-level command being used
    print("OS Interaction: using 'net user' to retrieve local accounts\n")

    # Retrieve the list of local users
    users = get_local_users()

    # If no users were found, fall back to current user only
    if not users:
        print("No user accounts detected via 'net user'.")
        print("Falling back to current user only.\n")
        users = [current_user]

    # Display header for user account list
    print("Local User Accounts:\n")

    # Loop through each user and display their privilege level and description
    for user in users:
        admin_status = is_admin(user)  # Check if user is an administrator
        label = "Administrator" if admin_status else "Standard User"  # Assign label
        description = PRIVILEGE_DESCRIPTIONS.get(label, "No description available.")  # Get description
        last_login = get_last_login(user)
        # Print the user and their privilege level
        print(f"- {user}: {label}")
        print(f"  Description: {description}\n")
        print(f"  Last Login: {last_login}\n")

# Run the main function only if the script is executed directly
if __name__ == "__main__":
    main()