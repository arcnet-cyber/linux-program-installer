import os
import time

from managers import get_manager

def clear_terminal():
    # For Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # For macOS and Linux
    else:
        _ = os.system('clear')

def detect_os():
    try:
        with open("/etc/os-release", "r") as f:
            for line in f:
                if line.startswith("ID="):
                    return line.strip().split("=")[1].strip('"')
    except FileNotFoundError:
        pass
    return "unknown"

def main():
    os_id = detect_os()
    try:
        manager = get_manager(os_id)
    except NotImplementedError as e:
        print(f"[!] Error: {e}")
        return

    clear_terminal()


    while True:
        print("Package Search & Install Tool")
        print("Type 'exit' to quit.\n")
        search_term = input("Enter program name to search: ").strip()
        if search_term.lower() == 'exit':
            print("Exiting.")
            clear_terminal()
            break

        results = manager.search_package(search_term)

        if not results:
            print("No packages found.\n")
            time.sleep(1.5)
            clear_terminal()
            continue

        # Split results into lines
        lines = results.strip().split('\n')
        package_options = []

        print("\nMatching Packages:")
        for idx, line in enumerate(lines):
            if '/' in line:
                name = line.split()[0].split('/')[-1]
                package_options.append(name)
                print(f"{idx + 1}. {line}")
            else:
                print(f"    {line}")  # Description line

        if not package_options:
            print("No valid packages to choose.\n")
            continue

        choice = input("\nSelect a package number to install (or 'skip'): ").strip()
        if choice.lower() == 'skip':
            continue

        try:
            idx = int(choice) - 1
            selected_pkg = package_options[idx]
        except (ValueError, IndexError):
            print("Invalid selection.\n")
            time.sleep(1.5)
            clear_terminal()
            continue

        print(f"\nSelected package: {selected_pkg}")

        confirm = input(f"Install '{selected_pkg}'? (y/n): ").strip().lower()
        if confirm == 'y':
            install_cmd = manager.generate_install_command([selected_pkg])
            print(f"Running: {install_cmd}")
            import subprocess
            subprocess.run(install_cmd.split())
        else:
            print("Skipped installation.")

        print("\n-----------------------------\n")
        time.sleep(1.5)
        clear_terminal()
if __name__ == "__main__":
    main()
