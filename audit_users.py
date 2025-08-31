# Import modules for OS interaction, subprocess execution, user info, and platform detection
import os
import subprocess
import getpass
import platform

# Import Windows COM interface for WMI queries
import win32com.client

# Import datetime for timestamp formatting
import datetime

# Import privilege descriptions from external dictionary file
from privileges import PRIVILEGE_DESCRIPTIONS

# Define a function to check if the OS is Windows
def is_windows():
    return platform.system() == "Windows"

# Define a function to retrieve local user accounts using 'net user'
def get_local_users():
    try:
        # Run the 'net user' command and capture its output
        result = subprocess.run(["net", "user"], capture_output=True, text=True)
        lines = result.stdout.splitlines()

        # Initialize list to store usernames
        users = []
        capture = False

        # Loop through each line of output
        for line in lines:
            # Start capturing usernames after this header line
            if "User accounts for" in line:
                capture = True
                continue
            # Stop capturing when command summary is reached
            if capture and ("The command completed successfully" in line or line.strip() == ""):
                break
            # Extract usernames from captured lines
            if capture:
                users.extend(line.strip().split())

        # Return the list of usernames
        return users

    # Handle any errors during command execution
    except Exception as e:
        print(f"Error retrieving users: {e}")
        return []

# Define a function to get the last login time for a user using WMI
def get_last_login(user):
    try:
        # Create a WMI locator object
        locator = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        # Connect to the WMI service
        services = locator.ConnectServer(".", "root\\cimv2")
        # Build a query to get login profile for the user
        query = f"SELECT * FROM Win32_NetworkLoginProfile WHERE Name = '{user}'"
        # Execute the query
        results = services.ExecQuery(query)

        # Loop through results and return the LastLogon value
        for item in results:
            if item.LastLogon:
                return item.LastLogon
        # Return fallback if no login time found
        return "Not available"
    # Handle any errors during WMI query
    except Exception as e:
        return f"Error retrieving login time: {e}"

# Define a function to format WMI timestamps into readable format
def format_wmi_timestamp(wmi_timestamp):
    # Return original if timestamp is missing or malformed
    if not wmi_timestamp or '.' not in wmi_timestamp:
        return wmi_timestamp
    # Extract the date portion before the decimal
    dt_str = wmi_timestamp.split('.')[0]
    try:
        # Parse the string into a datetime object
        dt = datetime.datetime.strptime(dt_str, "%Y%m%d%H%M%S")
        # Format the datetime into readable string
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    # Return original if parsing fails
    except Exception:
        return wmi_timestamp

# Define a function to check if a user is an administrator
def is_admin(user):
    try:
        # Run 'net user <username>' to get user details
        result = subprocess.run(["net", "user", user], capture_output=True, text=True)
        # Convert output to lowercase for easier matching
        output = result.stdout.lower()
        # Check if 'administrators' appears in the output
        return "administrators" in output
    # Handle any errors during command execution
    except Exception as e:
        print(f"Error checking admin status for {user}: {e}")
        return False

# Define a function to check if a user account is active or disabled
def get_account_status(user):
    try:
        # Run 'net user <username>' to get account status
        result = subprocess.run(["net", "user", user], capture_output=True, text=True)
        output = result.stdout.lower()

        # Loop through output lines to find account status
        for line in output.splitlines():
            if "account active" in line:
                # Return 'Active' or 'Disabled' based on value
                return "Active" if "yes" in line else "Disabled"
        # Return fallback if status not found
        return "Unknown"
    # Handle any errors during command execution
    except Exception as e:
        return f"Error: {e}"

# Define a function to get the full OS version string
def get_os_version():
    try:
        return platform.platform()
    # Handle any errors during platform query
    except Exception as e:
        return f"Error: {e}"

# Define the main function to run the audit
def main():
    # Get the OS type (e.g., Windows)
    os_type = platform.system()
    # Get the full OS version string
    os_version = get_os_version()

    # Print tool header
    print("User Privilege Audit Tool\n")
    # Print OS type and version
    print(f"Operating System: {os_type}")
    print(f"OS Version: {os_version}\n")

    # Get and print the current logged-in user
    current_user = getpass.getuser()
    print(f"Current User: {current_user}\n")

    # Exit if not running on Windows
    if not is_windows():
        print("This script currently supports Windows only.\n")
        return

    # Print the method used to retrieve user accounts
    print("OS Interaction: using 'net user' to retrieve local accounts\n")

    # Retrieve local user accounts
    users = get_local_users()

    # If no users found, fall back to current user only
    if not users:
        print("No user accounts detected via 'net user'.")
        print("Falling back to current user only.\n")
        users = [current_user]

    # Print table header for user details
    print("Local User Accounts:\n")
    print(f"{'User':<20} {'Privilege':<15} {'Status':<10} {'Last Login':<20}")
    print("-" * 70)

    # Loop through each user and print their details
    for user in users:
        # Check if user is an administrator
        admin_status = is_admin(user)
        # Assign privilege label based on admin status
        label = "Administrator" if admin_status else "Standard User"
        # Get account status (active/disabled)
        status = get_account_status(user)
        # Get raw last login timestamp
        last_login = get_last_login(user)
        # Format the timestamp into readable format
        last_login_fmt = format_wmi_timestamp(last_login)

        # Print formatted user details in table row
        print(f"{user:<20} {label:<15} {status:<10} {last_login_fmt:<20}")

    # Add spacing after output
    print("\n")

# Run the main function only if the script is executed directly
if __name__ == "__main__":
    main()