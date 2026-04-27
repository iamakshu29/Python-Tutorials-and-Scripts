# Call a REST API endpoint repeatedly and paginate until all results are collected.
# Pagination = splitting large datasets into pages
# APIs often do not return all records in one response because :
    # a. payload size limits
    # b. performance concerns
    # c. Rate limiting
# Instead, it returns
    # subset of results (a page)
    # Meta data on how to move to next page

# WORKFLOW
    # a. Make initial API call
    # b. Extract data from response
    # c. Store/append results
    # d. Check pagination signal:
    # e. next page? / next cursor? / more results?
    # f. If yes → make next request
    # g. If no → stop

import requests
all_results = []
page = 1
url = "https://api.github.com/repos/kubernetes/kubernetes/pulls"
payload = {"page":2,"per_page":100}


while True:
    res = requests.get("https://httpbin.org/get",params=payload)
    # print(res.ok)
    data = res.json()

    if not data:
        break

    all_results.append(data)
    page += 1

print(all_results)