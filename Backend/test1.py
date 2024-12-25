import requests

url = "http://127.0.0.1:2004/v1/embeddings"

headers = {
    "Content-Type": "application/json"
}
body = {
    "model": "text-embedding-nomic-embed-text-v1.5",
    "input": "Some text to embed"
}

resp = requests.post(url, headers=headers, json=body)

print(resp.json())