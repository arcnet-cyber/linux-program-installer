import subprocess
import os
from .base import PackageManager

class DnfManager(PackageManager):
    def search_package(self, name):
        env = os.environ.copy()
        env["LANG"] = "C"  # force consistent output

        # Optional: run makecache with sudo (comment if sudo not wanted)
        # subprocess.run(["sudo", "dnf", "makecache"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)

        result = subprocess.run(
            ["dnf", "search", name],
            capture_output=True,
            text=True,
            env=env
        )

        if result.returncode != 0:
            print("[!] dnf search failed:")
            print(result.stderr)
            return []

        lines = result.stdout.strip().splitlines()
        packages = []
        parsing = False

        for line in lines:
            line = line.strip()
            # Start parsing after the line with === (header separator)
            if line.startswith("===="):
                parsing = True
                continue
            if not parsing or not line:
                continue

            # Lines look like: pkgname.arch : description
            if " : " in line:
                pkg_part, desc = line.split(" : ", 1)
                pkg_name = pkg_part.split(".")[0]  # remove arch suffix
                packages.append((pkg_name, desc.strip()))

        return packages

    def validate_package(self, name):
        env = os.environ.copy()
        env["LANG"] = "C"

        result = subprocess.run(
            ["dnf", "info", name],
            capture_output=True,
            text=True,
            env=env
        )

        if result.returncode != 0:
            return False

        for line in result.stdout.splitlines():
            if line.strip().startswith("Name"):
                pkg_name = line.split(":", 1)[1].strip()
                return pkg_name == name
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
        names = [pkg for pkg, _ in packages]
        return f"sudo dnf install -y {' '.join(names)}"
