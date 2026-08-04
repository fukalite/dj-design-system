import json
import subprocess


query = """
query {
  repository(owner: "fukalite", name: "dj-design-system") {
    pullRequest(number: 89) {
      reviewThreads(first: 50) {
        nodes {
          id
          isResolved
          comments(first: 1) {
            nodes {
              databaseId
              body
            }
          }
        }
      }
    }
  }
}
"""

res = subprocess.run(["gh", "api", "graphql", "-f", f"query={query}"], capture_output=True, text=True)
data = json.loads(res.stdout)
threads = data["data"]["repository"]["pullRequest"]["reviewThreads"]["nodes"]

for thread in threads:
    if not thread["isResolved"]:
        thread_id = thread["id"]
        # 1. Add reply
        reply_mutation = """
        mutation($threadId: ID!, $body: String!) {
          addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: $threadId, body: $body}) {
            clientMutationId
          }
        }
        """
        subprocess.run([
            "gh", "api", "graphql", 
            "-F", f"threadId={thread_id}", 
            "-F", "body=Fixed in latest commit.", 
            "-f", f"query={reply_mutation}"
        ])
        
        # 2. Resolve thread
        resolve_mutation = """
        mutation($threadId: ID!) {
          resolveReviewThread(input: {threadId: $threadId}) {
            clientMutationId
          }
        }
        """
        subprocess.run([
            "gh", "api", "graphql", 
            "-F", f"threadId={thread_id}", 
            "-f", f"query={resolve_mutation}"
        ])
        print(f"Resolved thread {thread_id}")
