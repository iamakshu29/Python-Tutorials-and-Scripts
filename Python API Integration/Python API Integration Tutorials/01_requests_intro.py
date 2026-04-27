# 1_requests_intro.py — CRUD Operations & API Automation using `requests`

from json import JSONDecodeError
import requests
import csv
import json

baseURL = "https://fakestoreapi.com"
endpoint = "products"

# =============================================
# SYNTAX REFERENCE
# =============================================
# requests.get(url) / requests.post(url) / requests.delete(url)
# requests.request(method,url) -> method = "GET","POST","DELETE","PUT"

# =============================================
# NOTE: response.json() vs json.dumps()
# =============================================
# response.json() — parses JSON response into a Python object (dict/list)
# json.dumps() — converts a Python object back into a JSON string

# =============================================
# UTILITY: Centralized request handler
# =============================================
# All CRUD functions route through here — keeps error handling in one place.
# **kwargs passes extra args like json=body, headers=..., params=... to requests.
def make_request(method, path="",**kwargs):
  url = f"{baseURL}/{endpoint}{path}"
  try:
    response = requests.request(method,url,timeout=10,**kwargs)
    response.raise_for_status()  # Raises HTTPError for 4xx/5xx status codes
    return response
  except requests.exceptions.RequestException as e:
    print(f" Error: {e}")
    return
  except ValueError:
    print("Invalid response")
    return

# =============================================
# GET: Check status code
# =============================================
# Useful for verifying the API is reachable before processing data.
def get_status_code():
  response = make_request("GET")
  if response:
    print(response.status_code)
# get_status_code()


# =============================================
# GET: Fetch all products
# =============================================
# Returns a list of dicts — each dict is one product.
def get_products():
  response = make_request("GET")
  if response:
    data = response.json()  # Parses JSON response into a Python list of dicts
    print(data)   

    # json.dumps() converts Python object back to a formatted JSON string
    print(f"\nData at 0th Index is: {json.dumps(data[0], indent=2)}")

    print(f"\nTitle at 0th Index is: {data[0]["title"]}\n")

    # Inspect available keys on the first product
    for j in data[0].keys():
      print(f"- {j}")
# get_products()


# =============================================
# GET: Fetch single product by ID
# =============================================
# API returns an empty string for IDs > 20 — only 20 products exist.
def get_product_by_id(id):
  response = make_request("GET",f"/{id}")
  if not response:
    return
  try:
      data = response.json()
      print(data)
  except ValueError:  # .json() raises ValueError when the body is empty or not valid JSON
      print("Invalid or empty JSON response")
# get_product_by_id(1)
# get_product_by_id(21)


# =============================================
# POST: Add a new product
# =============================================
# json=body serializes the dict to JSON and sets Content-Type: application/json automatically.
def add_product():
  body = {
    "id":"21",
    "title":"innerwear",
    "price":150,
    "description":"Comfortable and soft",
    "category":"men",
    "image":"http://example.com"
  }
  return make_request("POST",json=body)
# print(add_product())


# =============================================
# PUT: Update product's title
# =============================================
# Fetches current data first — PUT replaces the full resource, so all fields must be sent.
def update_product_title(id):
  response = make_request("GET",f"/{id}")
  if response:
    print(f"Title Before {response.json()['title']}")

  body = response.json()
  body["title"] = "Innerwear"  # Modify only the target field, keep the rest unchanged

  response = make_request("PUT",f"/{id}",json=body)
  print(f"Title After {response.json()['title']}")
# update_product_title(1)

# =============================================
# DELETE: Remove a product by ID
# =============================================
def delete_product(id):
  response = make_request("DELETE",f"/{id}")
  if response:
    print(response.status_code)  # 200 indicates the resource was successfully deleted
# delete_product(1)


# =============================================
# PROJECT: API → CSV Automation
# =============================================
# Fetches all products and writes only id & title to a CSV file.
def save_fields_to_csv():
  response = make_request("GET")
  if response:
    data = response.json()

    with open("posts.csv", "w", newline="") as f:
      writer = csv.writer(f)
      writer.writerow(["id", "title"])  # Header row
      for i in data:
        writer.writerow([i["id"],i["title"]])
# save_fields_to_csv()