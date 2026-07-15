import requests

def fetch_github_code(repo_url: str) -> str:
    """
    Downloads all .py files from a public GitHub repo (including subfolders).
    Returns their contents concatenated as one string.
    Raises ValueError if the repo is unreachable or private.
    """

    # Step 1: Convert GitHub URL to API format
    parts = repo_url.rstrip('/').split('/')
    user = parts[-2]
    repo = parts[-1]

    code_parts = []
    total_chars = 0

    def fetch_folder(api_url):
        """Recursively fetch .py files from a folder."""
        nonlocal total_chars

        try:
            resp = requests.get(api_url, timeout=10)
        except requests.RequestException:
            raise ValueError("Could not connect to GitHub. Check the URL and try again.")

        if resp.status_code == 404:
            raise ValueError("Repo not found. It may be private or the URL is wrong.")
        if resp.status_code == 403:
            raise ValueError("GitHub API rate limit reached. Please try again later.")
        if resp.status_code != 200:
            raise ValueError("Repo not reachable. Please check the URL.")

        items = resp.json()

        for item in items:
            # Stop if 50,000 character limit reached
            if total_chars >= 50000:
                code_parts.append("# --- Limit reached: remaining files skipped ---")
                return

            if item["type"] == "file" and item["name"].endswith(".py"):
                try:
                    r = requests.get(item["download_url"], timeout=10)
                    content = f"# --- {item['name']} ---\n" + r.text

                    if total_chars + len(content) > 50000:
                        code_parts.append("# --- Limit reached: remaining files skipped ---")
                        return

                    code_parts.append(content)
                    total_chars += len(content)

                except requests.RequestException:
                    continue

            elif item["type"] == "dir":
                # Go into subfolders
                fetch_folder(item["url"])

    # Start from root
    root_api_url = f"https://api.github.com/repos/{user}/{repo}/contents"
    fetch_folder(root_api_url)

    if not code_parts:
        raise ValueError("No .py files found in this repo.")

    return "\n\n".join(code_parts)