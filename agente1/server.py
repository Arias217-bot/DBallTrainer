import requests

n8n_webhook_url = "http://localhost:5678/webhook-test/45a5f3f8-2f7c-48ed-a036-57ca4adedb91"
file_path = "./Usuarios.JSON"

with open(file_path, "rb") as file:
    files = {
        'data': file
    }

    response = requests.post(n8n_webhook_url, files=files)

print(response.status_code)
print(response.json())