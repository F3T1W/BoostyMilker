import os
import sys
import re
import subprocess
import shutil
import hashlib
import time
import requests

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION_FILE = os.path.join(PROJECT_ROOT, "pyproject.toml")
CHOCO_NUSPEC = os.path.join(PROJECT_ROOT, "chocolatey", "boosty-milker.nuspec")
DEBIAN_CONTROL = os.path.join(PROJECT_ROOT, "package", "DEBIAN", "control")
BREW_FORMULA = os.path.join(PROJECT_ROOT, "boosty-milker.rb")

def run_cmd(cmd, cwd=None):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Error executing {cmd}:\n{result.stderr}")
        sys.exit(1)
    return result.stdout.strip()

def get_current_version():
    with open(VERSION_FILE, "r") as f:
        content = f.read()
    match = re.search(r'version = "([\d\.]+)"', content)
    if match:
        return match.group(1)
    sys.exit("Could not find version in pyproject.toml")

def update_version_in_files(new_version):
    print(f"Updating version to {new_version}...")
    
    # 1. pyproject.toml is already updated if we are here? No, let's update it.
    with open(VERSION_FILE, "r") as f:
        content = f.read()
    new_content = re.sub(r'version = "[\d\.]+"', f'version = "{new_version}"', content)
    with open(VERSION_FILE, "w") as f:
        f.write(new_content)
        
    # 2. Chocolatey nuspec
    with open(CHOCO_NUSPEC, "r") as f:
        content = f.read()
    new_content = re.sub(r'<version>[\d\.]+</version>', f'<version>{new_version}</version>', content)
    with open(CHOCO_NUSPEC, "w") as f:
        f.write(new_content)
        
    # 3. Debian control
    with open(DEBIAN_CONTROL, "r") as f:
        content = f.read()
    new_content = re.sub(r'Version: [\d\.]+', f'Version: {new_version}', content)
    with open(DEBIAN_CONTROL, "w") as f:
        f.write(new_content)

def git_commit_and_tag(version):
    print("Committing and tagging...")
    run_cmd(f'git add .', cwd=PROJECT_ROOT)
    run_cmd(f'git commit -m "Bump version to {version}"', cwd=PROJECT_ROOT)
    run_cmd(f'git push origin main', cwd=PROJECT_ROOT)
    run_cmd(f'git tag v{version}', cwd=PROJECT_ROOT)
    run_cmd(f'git push origin v{version}', cwd=PROJECT_ROOT)

def wait_for_assets(version):
    print("Waiting for GitHub Actions to build assets (this may take 2-5 minutes)...")
    url = f"https://github.com/F3T1W/BoostyMilker/releases/download/v{version}/boosty-milker-linux"
    
    for i in range(30): # Wait up to 5 minutes
        response = requests.head(url)
        if response.status_code == 302 or response.status_code == 200:
            print("Assets are ready!")
            return
        time.sleep(10)
        print(".", end="", flush=True)
    
    print("\nAssets not found after waiting. Check GitHub Actions.")
    sys.exit(1)

def calculate_sha256(url):
    print(f"Downloading {url} to calculate hash...")
    response = requests.get(url, stream=True)
    sha256_hash = hashlib.sha256()
    for chunk in response.iter_content(4096):
        sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def update_brew_formula(version):
    tarball_url = f"https://github.com/F3T1W/BoostyMilker/archive/refs/tags/v{version}.tar.gz"
    sha = calculate_sha256(tarball_url)
    
    print(f"Updating Homebrew formula with SHA: {sha}")
    
    with open(BREW_FORMULA, "r") as f:
        content = f.read()
        
    content = re.sub(r'url ".*?"', f'url "{tarball_url}"', content)
    content = re.sub(r'sha256 ".*?"', f'sha256 "{sha}"', content)
    
    with open(BREW_FORMULA, "w") as f:
        f.write(content)

    # Push to tap
    tap_dir = os.path.join(os.path.dirname(PROJECT_ROOT), "homebrew-tap")
    if os.path.exists(tap_dir):
        shutil.copy(BREW_FORMULA, os.path.join(tap_dir, "boosty-milker.rb"))
        run_cmd('git add boosty-milker.rb', cwd=tap_dir)
        run_cmd(f'git commit -m "Update to {version}"', cwd=tap_dir)
        run_cmd('git push origin main', cwd=tap_dir)
        print("Homebrew tap updated!")
    else:
        print("Warning: homebrew-tap directory not found nearby. Skipping tap push.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/manager.py <new_version>")
        sys.exit(1)
        
    new_version = sys.argv[1]
    
    print(f"=== Starting release process for v{new_version} ===")
    
    # 1. Update version in local files
    update_version_in_files(new_version)
    
    # 2. Verify local build (optional but recommended)
    print("Verifying local pip install...")
    run_cmd("pip install .", cwd=PROJECT_ROOT)
    
    # 3. Commit and Tag
    git_commit_and_tag(new_version)
    
    # 4. Wait for GitHub to build binaries (so we can update hashes/download them)
    # Actually for Brew we only need source tarball which is available immediately after tag
    # But if we want to download binaries for APT/Chocolatey we need to wait.
    
    # For now, let's just update Brew immediately as it uses source
    update_brew_formula(new_version)
    
    print("\n=== Release v{new_version} initiated! ===")
    print("Next steps:")
    print("1. Wait for GitHub Actions to finish.")
    print("2. Run 'python3 -m twine upload dist/*' for PyPI (after 'python3 -m build')")
    print("3. For Chocolatey/APT: Download binaries from Release page and push manually (or automate later).")

if __name__ == "__main__":
    main()
