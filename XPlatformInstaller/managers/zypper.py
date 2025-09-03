import subprocess
from .base import PackageManager

class ZypperManager(PackageManager):
    def search_package(self, name):
        result = subprocess.run(
            ["zypper", "search", name],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()

    def validate_package(self, name):
        result = subprocess.run(
            ["zypper", "info", name],
            capture_output=True,
            text=True
        )
        return "Name" in result.stdout and "Summary" in result.stdout

    def clean_package_list(self, package_list):
        seen = set()
        valid = []
        for pkg in package_list:
            pkg = pkg.strip()
            if pkg and pkg not in seen:
                seen.add(pkg)
                if self.validate_package(pkg):
                    valid.append(pkg)
                else:
                    print(f"[!] Package not found: {pkg}")
        return valid

    def generate_install_command(self, package_list):
        return f"sudo zypper install -y {' '.join(package_list)}"
