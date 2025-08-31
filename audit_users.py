# Import standard Python modules
import os
import subprocess
import getpass
import platform
import win32com.client
import datetime

# Import privilege descriptions from external dictionary
from privileges import PRIVILEGE_DESCRIPTIONS

# Check if the script is running on a Windows system
def is_windows():
    return platform.system() == "Windows"

# Retrieve all local user accounts using the 'net user' command
def get_local_users():
    try:
        result = subprocess.run(["net", "user"], capture_output=True, text=True)
        lines = result.stdout.splitlines()

        users = []
        capture = False

        for line in lines:
            if "User accounts for" in line:
                capture = True
                continue
            if capture and ("The command completed successfully" in line or line.strip() == ""):
                break
            if capture:
                users.extend(line.strip().split())

        return users

    except Exception as e:
        print(f"Error retrieving users: {e}")
        return []

# Get the last login time for a specific user using WMI
def get_last_login(user):
    try:
        locator = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        services = locator.ConnectServer(".", "root\\cimv2")
        query = f"SELECT * FROM Win32_NetworkLoginProfile WHERE Name = '{user}'"
        results = services.ExecQuery(query)

        for item in results:
            if item.LastLogon:
                return item.LastLogon
        return "Not available"
    except Exception as e:
        return f"Error retrieving login time: {e}"

# Convert WMI timestamp to human-readable format
def format_wmi_timestamp(wmi_timestamp):
    if not wmi_timestamp or '.' not in wmi_timestamp:
        return wmi_timestamp
    dt_str = wmi_timestamp.split('.')[0]
    try:
        dt = datetime.datetime.strptime(dt_str, "%Y%m%d%H%M%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return wmi_timestamp

# Check if a user is part of the Administrators group
def is_admin(user):
    try:
        result = subprocess.run(["net", "user", user], capture_output=True, text=True)
        output = result.stdout.lower()
        return "administrators" in output
    except Exception as e:
        print(f"Error checking admin status for {user}: {e}")
        return False

# Determine if a user account is active or disabled
def get_account_status(user):
    try:
        result = subprocess.run(["net", "user", user], capture_output=True, text=True)
        output = result.stdout.lower()
        for line in output.splitlines():
            if "account active" in line:
                return "Active" if "yes" in line else "Disabled"
        return "Unknown"
    except Exception as e:
        return f"Error: {e}"

# Retrieve the OS version string
def get_os_version():
    try:
        return platform.platform()
    except Exception as e:
        return f"Error: {e}"

# Main function that runs the audit and prints user info
def main():
    os_type = platform.system()
    os_version = get_os_version()

    print("User Privilege Audit Tool\n")
    print(f"Operating System: {os_type}")
    print(f"OS Version: {os_version}\n")

    current_user = getpass.getuser()
    print(f"Current User: {current_user}\n")

    if not is_windows():
        print("This script currently supports Windows only.\n")
        return

    print("OS Interaction: using 'net user' to retrieve local accounts\n")

    users = get_local_users()

    if not users:
        print("No user accounts detected via 'net user'.")
        print("Falling back to current user only.\n")
        users = [current_user]

    print("Local User Accounts:\n")
    print(f"{'User':<20} {'Privilege':<15} {'Status':<10} {'Last Login':<20}")
    print("-" * 70)

    for user in users:
        admin_status = is_admin(user)
        label = "Administrator" if admin_status else "Standard User"
        status = get_account_status(user)
        last_login = get_last_login(user)
        last_login_fmt = format_wmi_timestamp(last_login)

        print(f"{user:<20} {label:<15} {status:<10} {last_login_fmt:<20}")

    print("\n")

# Run the main function only if the script is executed directly
if __name__ == "__main__":
    main()