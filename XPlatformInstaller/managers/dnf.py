import subprocess
from .base import PackageManager

class DnfManager(PackageManager):
    def search_package(self, name):
        result = subprocess.run(
            ["dnf", "search", name],
            capture_output=True,
            text=True
        )
        lines = result.stdout.strip().splitlines()

        packages = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("Last metadata expiration check") or line.startswith("DNF") or line.startswith("Name") or line.startswith("--"):
                continue
            # Lines usually look like: package-name.arch : Description
            if " : " in line:
                pkg_part, desc = line.split(" : ", 1)
                # Package name may include arch (e.g. bash.x86_64)
                pkg_name = pkg_part.split(".")[0].strip()
                packages.append((pkg_name, desc.strip()))
        return packages

    def validate_package(self, name):
        result = subprocess.run(
            ["dnf", "info", name],
            capture_output=True,
            text=True
        )
        output = result.stdout.strip()
        # If package info found, output usually contains "Name : <package>"
        return f"Name    : {name}" in output or f"Name : {name}" in output

    def clean_package_list(self, package_list):
        seen = set()
        valid = []
        for pkg, desc in package_list:
            if pkg not in seen:
                seen.add(pkg)
                if self.validate_package(pkg):
                    valid.append((pkg, desc))
                else:
                    print(f"[!] Package not found or not installable: {pkg}")
        return valid

    def generate_install_command(self, packages):
        names = [pkg for pkg, _ in packages]
        return f"sudo dnf install -y {' '.join(names)}"
