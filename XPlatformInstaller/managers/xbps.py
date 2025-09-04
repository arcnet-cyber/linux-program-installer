import subprocess
import re
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
            s = line.strip()
            if not s:
                continue

            # Remove leading status token like "[-]" or "[I]"
            if s.startswith("["):
                rb = s.find("]")
                if rb != -1:
                    s = s[rb+1:].lstrip()

            # First token should now be "repo/pkgver" or just "pkgver"
            first, rest = (s.split(None, 1) + [""])[:2]

            # Drop repo prefix if present
            pkgver = first.split("/", 1)[-1]

            # Convert "name-1.2.3_1" -> "name"
            cut = None
            for i in range(len(pkgver) - 2, -1, -1):
                if pkgver[i] == '-' and i + 1 < len(pkgver) and pkgver[i + 1].isdigit():
                    cut = i
                    break
            pkg_name = pkgver[:cut] if cut is not None else pkgver

            # Clean description: remove leading arch token and/or [installed]
            desc = rest.strip()
            if desc:
                first2, rest2 = (desc.split(None, 1) + [""])[:2]
                if first2 in ("x86_64", "x86_64-musl", "i686", "i686-musl",
                              "aarch64", "armv7hf", "noarch"):
                    desc = rest2.strip()
                desc = re.sub(r"^\[installed\]\s*", "", desc).strip()

            packages.append((pkg_name, desc or ""))

        return packages

    def validate_package(self, name):
        # Return True if any package matches the base name
        result = subprocess.run(
            ["xbps-query", "-Rs", name],
            capture_output=True,
            text=True
        )
        lines = result.stdout.strip().splitlines()
        for line in lines:
            if not line.strip():
                continue
            # Extract the package name portion
            first = line.strip().split(None, 1)[0].split("/", 1)[-1]
            # Remove version suffix
            pkg_base = re.sub(r"-\d.*$", "", first)
            if pkg_base == name:
                return True
        return False

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
        # Resolve the actual full package names for installation
        resolved_names = []
        for pkg, _ in packages:
            result = subprocess.run(
                ["xbps-query", "-Rs", pkg],
                capture_output=True,
                text=True
            )
            lines = result.stdout.strip().splitlines()
            if lines:
                # Take first match and drop repo prefix
                first_pkg = lines[0].split(None, 1)[0].split("/", 1)[-1]
                resolved_names.append(first_pkg)
        return f"sudo xbps-install -Sy {' '.join(resolved_names)}"
