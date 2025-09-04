import os
import platform
from managers import get_manager
import subprocess

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def pause():
    input("\nPress Enter to continue...")

def detect_os_id():
    try:
        with open("/etc/os-release", "r") as f:
            for line in f:
                if line.startswith("ID="):
                    return line.strip().split("=")[1].strip('"')
    except FileNotFoundError:
        return None
    return None

def main():
    os_id = detect_os_id()
    if not os_id:
        print("Unable to detect operating system.")
        return

    try:
        manager = get_manager(os_id)
    except NotImplementedError as e:
        print(str(e))
        return

    while True:
        clear_screen()
        print("Package Search & Install Tool")
        print("Type 'exit' to quit.\n")

        search_term = input("Enter program name to search: ").strip()
        if search_term.lower() == "exit":
            break

        results = manager.search_package(search_term)

        if not results:
            print("No matching packages found.")
            pause()
            continue

        print("\nMatching Packages:")
        for i, (pkg, desc) in enumerate(results, 1):
            print(f"  {i}. {pkg} - {desc}")

        choice = input("\nSelect a package to install [number or 'skip']: ").strip()

        if choice.lower() == "skip":
            continue

        if not choice.isdigit() or not (1 <= int(choice) <= len(results)):
            clear_screen()
            print("Invalid selection.")
            pause()
            continue

        selected = [results[int(choice) - 1]]
        cleaned = manager.clean_package_list(selected)

        if not cleaned:
            print("No valid packages to choose.")
            pause()
            continue

        print("Valid packages:", ', '.join(pkg for pkg, _ in cleaned))
        print("Install command:", manager.generate_install_command(cleaned))

        confirm = input("\nWould you like to run this install command now? [y/N]: ").strip().lower()
        if confirm == "y":
            subprocess.run(manager.generate_install_command(cleaned), shell=True)

        pause()

if __name__ == "__main__":
    main()
