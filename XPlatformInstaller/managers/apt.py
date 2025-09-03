import subprocess
from .base import PackageManager

class AptManager(PackageManager):
    def search_package(self, name):
        result = subprocess.run(
            ["apt-cache", "search", name],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip()

    def validate_package(self, name):
        # apt-cache policy returns info if package exists
        result = subprocess.run(
            ["apt-cache", "policy", name],
            capture_output=True,
            text=True,
            check=False,
        )
        # If the package has candidate version info, it exists
        return "Candidate:" in result.stdout and "none" not in result.stdout

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
        return f"sudo apt install -y {' '.join(package_list)}"
