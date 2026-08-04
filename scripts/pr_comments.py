import argparse
import json
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and display unresolved PR comments."
    )
    parser.add_argument(
        "pr_number",
        nargs="?",
        help="PR number (optional, defaults to current branch PR)",
    )
    args = parser.parse_args()

    cmd = ["gh", "pr", "view"]
    if args.pr_number:
        cmd.append(args.pr_number)

    cmd.extend(["--json", "comments,reviews", "-q", "."])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(
            f"Error fetching PR data (are you authenticated with 'gh'?): {e.stderr}",
            file=sys.stderr,
        )
        sys.exit(1)

    data = json.loads(result.stdout)
    comments = data.get("comments", [])

    unresolved_found = False
    for comment in comments:
        unresolved_found = True
        author = comment.get("author", {}).get("login", "Unknown")
        body = comment.get("body", "")
        created_at = comment.get("createdAt", "")
        print(f"\033[1;36m[{created_at}]\033[0m \033[1;33m{author}:\033[0m\n{body}\n")
        print("-" * 40)

    if not unresolved_found:
        print("\033[1;32mNo comments found! 🎉\033[0m")


if __name__ == "__main__":
    main()
