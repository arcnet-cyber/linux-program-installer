import subprocess
from .base import PackageManager

class XbpsManager(PackageManager):
    def search_package(self, name):
        result = subprocess.run(
            ["xbps-query", "-Rs", name],
            capture_output=True,
            text=True
        )
        lines = result.stdout.strip().splitlines()

        packages = []
        for line in lines:
            # Format: repository/package-version_arch [installed] <desc>
            # Example: void-repo/gparted-1.1.0_1  x86_64  [installed]  GNOME partition editor
            parts = line.split(None, 3)
            if len(parts) == 4:
                pkg_ver = parts[0]  # e.g. void-repo/gparted-1.1.0_1
                desc = parts[3]

                # Drop repo prefix
                if "/" in pkg_ver:
                    pkg_ver = pkg_ver.split("/", 1)[1]  # gparted-1.1.0_1

                # Remove version suffix (everything after the last dash followed by digits/underscore)
                base_parts = pkg_ver.split("-")
                while base_parts and (base_parts[-1].replace("_", "").isdigit() or base_parts[-1][0].isdigit()):
                    base_parts.pop()
                pkg_name = "-".join(base_parts)

                packages.append((pkg_name, desc))
        return packages

    def validate_package(self, name):
        result = subprocess.run(
            ["xbps-query", "-Rn", name],
            capture_output=True,
            text=True
        )
        return result.returncode == 0 and bool(result.stdout.strip())

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
        return f"sudo xbps-install -Sy {' '.join(names)}"
