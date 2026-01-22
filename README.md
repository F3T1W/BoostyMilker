# Boosty Milker 🥛

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/F3T1W/BoostyMilker)](https://github.com/F3T1W/BoostyMilker/releases)
[![PyPI version](https://img.shields.io/pypi/v/boosty-milker)](https://pypi.org/project/boosty-milker/)
[![Chocolatey Version](https://img.shields.io/chocolatey/v/boosty-milker)](https://community.chocolatey.org/packages/boosty-milker)
[![Homebrew](https://img.shields.io/badge/homebrew-tap-orange)](https://github.com/F3T1W/homebrew-tap)
[![APT](https://img.shields.io/badge/debian-apt-red)](https://github.com/F3T1W/apt-repo)

**Boosty Milker** is a powerful cross-platform CLI tool to bulk download photos from Boosty.to creators.

🚀 **Features:**
*   📥 Download all photos from all posts of a creator.
*   🔓 Support for premium/subscriber-only content (via auth token).
*   ⚡ Async downloads (fast and efficient).
*   🖥️ Works on **Windows, macOS, and Linux**.
*   💾 Smart download (skips already existing files).

---

## 📦 Installation

### 🍎 macOS (Homebrew)
The easiest way for Mac users:
```bash
brew tap F3T1W/tap
brew install boosty-milker
```

### 🐧 Linux (Debian / Ubuntu / APT)
Add the repository and install:
```bash
echo "deb [trusted=yes] https://F3T1W.github.io/apt-repo stable main" | sudo tee /etc/apt/sources.list.d/f3t1w.list
sudo apt-get update
sudo apt-get install boosty-milker
```
*Alternatively, download the `.deb` file manually from [Releases](https://github.com/F3T1W/BoostyMilker/releases).*

### 🪟 Windows (Chocolatey)
Install via PowerShell:
```powershell
choco install boosty-milker
```

### 🐍 Python (PIP)
Universal method for any OS (requires Python 3.10+):
```bash
pip install boosty-milker
```

### 📁 Manual Binaries
If you don't want to install anything, just download the executable for your OS from **[Releases](https://github.com/F3T1W/BoostyMilker/releases)**, place it in a convenient folder, and run it via terminal.

---

## 🚀 Usage

### 1. Download Free Posts
```bash
boosty-milker --username "artist_name" --directory "./downloads"
```
* `artist_name` — creator's username from the URL (e.g., for `boosty.to/cool_art` the username is `cool_art`).
* `directory` — folder to save photos.

### 2. Download Premium Content (Subscribers)
If you are subscribed to a creator, you need to provide your auth token to download private posts.

1.  Open [Boosty.to](https://boosty.to) in your browser.
2.  Press `F12` -> Go to **Application** (or Storage) tab.
3.  In the left menu, select **Cookies** -> `https://boosty.to`.
4.  Find the cookie named `auth_token` or `accessToken` and copy its value.

Run:
```bash
boosty-milker --username "artist_name" --directory "./downloads" --auth_token "YOUR_TOKEN"
```

### All Arguments
```text
options:
  -h, --help            show this help message
  --username USERNAME   Boosty creator username (from URL)
  --directory DIRECTORY Directory to save photos
  --auth_token TOKEN    Auth token (Bearer/accessToken) for private content
  --max_concurrency N   Number of concurrent downloads (default: 10)
```

---

## ⚠️ Disclaimer
This tool is for personal use only. Please only download content you have legal access to. The author is not responsible for any misuse of this software or violations of Boosty.to terms of service.

---

Made with ❤️ by [F3T1W](https://github.com/F3T1W)
