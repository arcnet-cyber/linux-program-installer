import subprocess
from .base import PackageManager


class AptManager(PackageManager):
    def search_package(self, name):
        result = subprocess.run(
            ["apt-cache", "search", name],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()

    def validate_package(self, name):
        result = subprocess.run(
            ["apt-cache", "policy", name],
            capture_output=True,
            text=True
        )
        output = result.stdout.strip()
        # Must have a valid installable candidate version
        return "Candidate:" in output and "none" not in output

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
                    print(f"[!] Package not found or not installable: {pkg}")
        return valid

    def generate_install_command(self, packages):
        return f"sudo apt install {' '.join(packages)}"
