import subprocess
from .base import PackageManager

class XbpsManager(PackageManager):
    def search_package(self, name):
        """
        Search for packages matching 'name' using xbps-query.
        Returns a list of tuples: (package_name, description)
        """
        result = subprocess.run(
            ["xbps-query", "-Rs", name],
            capture_output=True,
            text=True
        )
        lines = result.stdout.strip().splitlines()
        packages = []

        for line in lines:
            s = line.strip()
            if not s:
                continue

            # Remove leading status token like "[-]" or "[I]"
            if s.startswith("["):
                rb = s.find("]")
                if rb != -1:
                    s = s[rb+1:].lstrip()

            # First token is repo/package-version
            first, rest = (s.split(None, 1) + [""])[:2]

            # Remove repo prefix
            pkg_full = first.split("/", 1)[-1]  # e.g., "thc-hydra-9.4_1"

            # Remove version suffix for display and validation
            if "-" in pkg_full:
                pkg_name = "-".join(pkg_full.split("-")[:-1])  # "thc-hydra"
            else:
                pkg_name = pkg_full

            desc = rest.strip()
            packages.append((pkg_name, desc))

        return packages

    def validate_package(self, name):
        """
        Validate that a package exists in the repository.
        """
        result = subprocess.run(
            ["xbps-query", "-Rn", name],
            capture_output=True,
            text=True
        )
        return result.returncode == 0 and bool(result.stdout.strip())

    def clean_package_list(self, package_list):
        """
        Remove duplicates and invalid packages.
        """
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
        """
        Return a string for use with subprocess.run(shell=True)
        """
        names = [pkg for pkg, _ in packages]
        return f"sudo xbps-install -Sy {' '.join(names)}"
