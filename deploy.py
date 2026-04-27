import subprocess
import os
from config import GITHUB_REPO, GITHUB_PAGES_BRANCH, GITHUB_PAGES_SOURCE

REPO_DIR = os.path.join(os.path.dirname(__file__), "repo")

def deploy(html_content, week_ending):
    # Ensure gh-pages branch exists
    _ensure_branch()
    # Write to docs/
    docs_dir = os.path.join(REPO_DIR, GITHUB_PAGES_SOURCE)
    os.makedirs(docs_dir, exist_ok=True)
    html_file = os.path.join(docs_dir, "index.html")
    with open(html_file, "w") as f:
        f.write(html_content)
    # Commit and push
    subprocess.run(["git", "add", "."], cwd=REPO_DIR, check=False)
    result = subprocess.run(
        ["git", "commit", "-m", f"EV Digest {week_ending}"],
        cwd=REPO_DIR,
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        subprocess.run(
            ["git", "push", "-u", "origin", f"{GITHUB_PAGES_BRANCH}:{GITHUB_PAGES_BRANCH}"],
            cwd=REPO_DIR,
            capture_output=True, text=True,
        )
        print(f"  [deploy] pushed to gh-pages")
    else:
        if "nothing to commit" in result.stdout or result.returncode == 0:
            print(f"  [deploy] no changes to push")
        else:
            print(f"  [deploy] commit error: {result.stderr}")
            # Try force-add
            subprocess.run(["git", "add", "-f", "docs/"], cwd=REPO_DIR, check=False)
            subprocess.run(
                ["git", "commit", "-m", f"EV Digest {week_ending}"],
                cwd=REPO_DIR, capture_output=True, text=True,
            )
            subprocess.run(
                ["git", "push", "-u", "origin", f"{GITHUB_PAGES_BRANCH}:{GITHUB_PAGES_BRANCH}"],
                cwd=REPO_DIR, capture_output=True, text=True,
            )

def _ensure_branch():
    os.makedirs(REPO_DIR, exist_ok=True)
    if not os.path.exists(os.path.join(REPO_DIR, ".git")):
        subprocess.run(["git", "clone", "--branch", GITHUB_PAGES_BRANCH,
                        f"git@github.com:{GITHUB_REPO}.git", REPO_DIR],
                       capture_output=True, text=True)
        if subprocess.run(["git", "checkout", GITHUB_PAGES_BRANCH],
                        cwd=REPO_DIR, capture_output=True).returncode != 0:
            subprocess.run(["git", "checkout", "-b", GITHUB_PAGES_BRANCH], cwd=REPO_DIR)
    # Verify docs dir exists
    docs_dir = os.path.join(REPO_DIR, GITHUB_PAGES_SOURCE)
    os.makedirs(docs_dir, exist_ok=True)