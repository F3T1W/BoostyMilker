# Boosty Milker - Photo Downloader

CLI utility to download photos from Boosty.to creators. Supports downloading from both free and premium posts (with authentication).

## Installation

### Via PIP
```bash
pip install .
```

### Manual
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python src/main.py --help`

## Usage

### Basic (Free posts)
```bash
boosty-milker --username "artist_name" --directory "./downloads"
```

### Premium Content (Auth required)
1. Login to Boosty.to in your browser.
2. Open Developer Tools (F12) -> Application -> Cookies.
3. Copy the value of `auth_token` or `accessToken`.
4. Run:
```bash
boosty-milker --username "artist_name" --directory "./downloads" --auth_token "YOUR_TOKEN"
```

### Arguments
- `--username`: The creator's username (from their profile URL).
- `--directory`: Path to save images.
- `--auth_token`: (Optional) Access token for private posts.
- `--max_concurrency`: (Optional) Number of simultaneous downloads (default 10).
