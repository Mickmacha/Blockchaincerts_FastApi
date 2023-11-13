import requests

url = "http://127.0.0.1:8000/certificates"
params = {
        "name": "Dave Omollo",
        "issuer": "New York Giants",
        "issue_date": 19825699889,
        "certificate_id": "123"
    }
response = requests.get(url, params=params)

if response.status_code == 200:
    # Save the HTML content to a file
    with open("example.html", "w", encoding="utf-8") as file:
        file.write(response.text)
    print("HTML response saved to example.html")
else:
    print(f"Request failed with status code: {response.status_code}")