# Dictionary mapping privilege labels to descriptions
PRIVILEGE_DESCRIPTIONS = {
    "Administrator": "Full system access: can install software, manage users, and change settings.",
    "Standard User": "Limited access: can run applications and change personal settings, but not system-wide configurations.",
    "Guest": "Minimal access: temporary use with very restricted permissions."
}
# Import required modules
import os                     # For OS-level interactions
import subprocess             # To run system commands and capture output
import getpass                # To get the current logged-in user
import platform               # To detect the operating system
from privileges import PRIVILEGE_DESCRIPTIONS  # Import privilege descriptions

# Function to check if the script is running on Windows
def is_windows():
    return platform.system() == "Windows"

# Function to retrieve all local user accounts using 'net user'
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

# Function to check if a user is part of the Administrators group
def is_admin(user):
    try:
        result = subprocess.run(["net", "user", user], capture_output=True, text=True)
        output = result.stdout.lower()
        return "administrators" in output
    except Exception as e:
        print(f"Error checking admin status for {user}: {e}")
        return False

# Main function to run the audit
def main():
    os_type = platform.system()

    print("User Privilege Audit Tool")
    print()

    print(f"Operating System: {os_type}")
    current_user = getpass.getuser()
    print(f"Current User: {current_user}")
    print()

    if not is_windows():
        print("This script currently supports Windows only.")
        print()
        return

    print("OS Interaction: using 'net user' to retrieve local accounts")
    print()

    users = get_local_users()
    print("Local User Accounts:")
    print()

    for user in users:
        admin_status = is_admin(user)
        label = "Administrator" if admin_status else "Standard User"
        description = PRIVILEGE_DESCRIPTIONS.get(label, "No description available.")

        print(f"- {user}: {label}")
        print(f"  Description: {description}")
        print()

# Run the script only if executed directly
if __name__ == "__main__":
    main()