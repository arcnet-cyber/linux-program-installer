import os
import subprocess
from managers import get_manager

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

def run_install(manager, page_size=20):
    while True:
        clear_screen()
        print("Package Install Tool")
        print("Type 'exit' to quit.\n")

        search_term = input("Enter program name to search: ").strip()
        if search_term.lower() == "exit":
            break

        results = manager.search_package(search_term)
        if not results:
            print("No matching packages found.")
            pause()
            continue

        # Pagination if search returns many results
        page = 0
        total_pages = (len(results) + page_size - 1) // page_size

        while True:
            clear_screen()
            start = page * page_size
            end = start + page_size
            current_page = results[start:end]

            print(f"Package Install Tool (Search: {search_term})")
            print("Type 'exit' to quit, '>' next page, '<' previous page\n")

            for i, (pkg, desc) in enumerate(current_page, start=start + 1):
                print(f"{i}. {pkg} - {desc}")

            print(f"\nPage {page + 1} of {total_pages}")
            choice = input("\nSelect a package to install [number, '>', '<', 'exit']: ").strip()

            if choice.lower() == "exit":
                break
            elif choice == ">" and page < total_pages - 1:
                page += 1
                continue
            elif choice == "<" and page > 0:
                page -= 1
                continue
            elif choice.isdigit():
                num = int(choice)
                if 1 <= num <= len(results):
                    selected = [results[num - 1]]
                    cleaned = manager.clean_package_list(selected)
                    if not cleaned:
                        print("No valid packages to install.")
                        pause()
                        continue

                    cmd = manager.generate_install_command(cleaned)
                    print("Install command:", cmd)
                    confirm = input("Run install command now? [y/N]: ").strip().lower()
                    if confirm == "y":
                        subprocess.run(cmd, shell=True)
                    pause()
                    break
                else:
                    print("Number out of range.")
                    pause()
            else:
                print("Invalid input.")
                pause()

def run_uninstall(manager, page_size=20):
    packages = manager.list_installed_packages()
    if not packages:
        print("No installed packages found.")
        pause()
        return

    page = 0
    total_pages = (len(packages) + page_size - 1) // page_size

    while True:
        clear_screen()
        print("Package Uninstall Tool")
        print("Type 'exit' to quit, '>' next page, '<' previous page\n")

        start = page * page_size
        end = start + page_size
        current_page = packages[start:end]

        for i, (pkg, desc) in enumerate(current_page, start=start + 1):
            print(f"{i}. {pkg} {('- ' + desc) if desc else ''}")

        print(f"\nPage {page + 1} of {total_pages}")
        choice = input("\nSelect a package to uninstall [number, '>', '<', 'exit']: ").strip()

        if choice.lower() == "exit":
            break
        elif choice == ">" and page < total_pages - 1:
            page += 1
            continue
        elif choice == "<" and page > 0:
            page -= 1
            continue
        elif choice.isdigit():
            num = int(choice)
            if 1 <= num <= len(packages):
                selected = [packages[num - 1]]  # global index
                cleaned = manager.clean_package_list(selected)
                if not cleaned:
                    print("No valid packages to uninstall.")
                    pause()
                    continue

                cmd = manager.generate_uninstall_command(cleaned)
                print("Uninstall command:", cmd)
                confirm = input("Run uninstall command now? [y/N]: ").strip().lower()
                if confirm == "y":
                    subprocess.run(cmd, shell=True)
                pause()
            else:
                print("Number out of range.")
                pause()
        else:
            print("Invalid input.")
            pause()

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

    clear_screen()
    action = input("Would you like to [i]nstall or [u]ninstall packages? ").strip().lower()
    if action == "i":
        run_install(manager)
    elif action == "u":
        run_uninstall(manager)
    else:
        print("Invalid option.")

if __name__ == "__main__":
    main()
