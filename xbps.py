import subprocess
from .base import PackageManager

class XbpsManager(PackageManager):
    def search_package(self, name):
        """
        Search for packages matching 'name' using xbps-query.
        Returns a list of tuples: (base_name, description)
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

            # First token is repo/pkg-version
            first, rest = (s.split(None, 1) + [""])[:2]

            # Use just the base package name (drop repo & version)
            pkg_base = first.split("/", 1)[-1].split("-", 1)[0]

            # Description is the rest of the line
            desc = rest.strip()

            packages.append((pkg_base, desc))

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
        Generate a full xbps-install command for the given packages.
        """
        names = [pkg for pkg, _ in packages]
        return f"sudo xbps-install -Sy {' '.join(names)}"
