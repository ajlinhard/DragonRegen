import requests
import json

base_url = 'http://localhost:5000'

new_book = {
    "title": "Dune",
    "author": "Frank Herbert",
    "isbn": "9780441172719"
}

# For debugging, print what you're trying to send
print("Sending data:", json.dumps(new_book))

# Try this explicit approach
headers = {'Content-Type': 'application/json; charset=utf-8'}
response = requests.post(
    f'{base_url}/books',
    json=new_book,  # Convert dict to JSON string
    headers=headers
)

print("Status code:", response.status_code)
print("Response:", response.text)