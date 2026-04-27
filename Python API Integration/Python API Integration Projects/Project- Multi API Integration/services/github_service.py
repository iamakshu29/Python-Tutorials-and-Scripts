from clients.http_client import get_info

git_url = "https://api.github.com/users"

def fetch_user(username,headers):
    url  = f"{git_url}/{username}"
    return get_info(url,headers=headers)

def fetch_repos(username, headers, per_page=30):
    url = f"{git_url}/{username}/repos?per_page={per_page}"
    return get_info(url, headers=headers)

# GITHUB API
def get_top_repos(repo_data, limit=10):
    repos = [
        (repo["name"], repo["stargazers_count"])
        for repo in repo_data
    ]
    repos.sort(key=lambda x: x[1], reverse=True)
    return repos[:limit]

