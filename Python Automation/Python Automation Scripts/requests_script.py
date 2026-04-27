# Tasks:
# Call GitHub API and list open PRs.
# Call a public REST API and extract specific fields.

import requests

url = "https://api.github.com/repos/kubernetes/kubernetes/pulls"

def get_user(url):
    response = requests.get(url, timeout=5)
    if response.status_code == 200:

        # Convert the JSON response to a dictionary
        pull_requests = response.json()

        # Create an empty dictionary to store PR creators and their counts
        pr_creators = {}

        # Iterate through each pull request and extract the creator's name
        for pull in pull_requests:
            creator = pull['user']['login']
            if creator in pr_creators:
                pr_creators[creator] += 1
            else:
                pr_creators[creator] = 1
        # Display the dictionary of PR creators and their counts
        print("PR Creators and Counts:")
        for creator, count in pr_creators.items(): # loop over dict to get keys and values
            print(f"{creator}: {count} PR(s)")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

# get_user(url)