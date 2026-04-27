# merge data retrieve from both APIs
def build_output(username, city_data, temp, public_repos_count, top_repos):
    return{
        "developer": {
            "username": username,
            "public_repos": public_repos_count,
            "top_10_repos": [
                {"name": item[0], "stars": item[1]} for item in top_repos[:10]
            ]
        },
        "location_weather": {
            "city": city_data['name'],
            "temperature": temp,
            "condition": city_data['weather'][0]['description']
        }
    }