import json
import subprocess
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Fetch and display unresolved PR comments.")
    parser.add_argument("pr_number", nargs="?", help="PR number (optional, defaults to current branch PR)")
    args = parser.parse_args()

    cmd = ["gh", "pr", "view"]
    if args.pr_number:
        cmd.append(args.pr_number)
    
    cmd.extend(["--json", "reviewThreads", "-q", "."])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error fetching PR data (are you authenticated with 'gh'?): {e.stderr}", file=sys.stderr)
        sys.exit(1)
        
    data = json.loads(result.stdout)
    threads = data.get("reviewThreads", [])
    
    unresolved_found = False
    for thread in threads:
        if not thread.get("isResolved", False):
            unresolved_found = True
            comments = thread.get("comments", [])
            if not comments:
                continue
            
            # Print the context of the first comment
            first = comments[0]
            path = first.get("path", "Unknown file")
            print(f"\n\033[1;36m[{path}]\033[0m")
            
            for comment in comments:
                author = comment.get("author", {}).get("login", "Unknown")
                body = comment.get("body", "")
                print(f"\033[1;33m{author}:\033[0m\n{body}\n")
            print("-" * 40)

    if not unresolved_found:
        print("\033[1;32mNo unresolved comments found! 🎉\033[0m")

if __name__ == "__main__":
    main()
