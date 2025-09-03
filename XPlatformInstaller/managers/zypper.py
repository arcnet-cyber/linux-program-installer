import subprocess
from .base import PackageManager

class ZypperManager(PackageManager):
    def search_package(self, name):
        result = subprocess.run(
            ["zypper", "search", "-s", name],
            capture_output=True,
            text=True
        )
        lines = result.stdout.strip().splitlines()

        packages = []
        parsing = False

        for line in lines:
            line = line.strip()
            # Zypper search output has a header separated by lines like '---' 
            # We'll start parsing after we detect the header line
            if line.startswith("S | Name"):
                parsing = True
                continue
            if not parsing or line.startswith("---") or not line:
                continue

            # Format: S | Name        | Type    | Version      | Arch   | Repository
            # We'll split by '|' and strip whitespace
            parts = [part.strip() for part in line.split("|")]
            if len(parts) >= 2:
                pkg_name = parts[1]
                # We can try to get description by querying zypper info if needed,
                # but for now, leave description empty or just name
                packages.append((pkg_name, "No description available"))
        return packages

    def validate_package(self, name):
        result = subprocess.run(
            ["zypper", "info", name],
            capture_output=True,
            text=True
        )
        output = result.stdout.strip()
        # If package exists, output contains "Information for package <name>"
        return f"Information for package {name}" in output

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
        return f"sudo zypper install -y {' '.join(names)}"
