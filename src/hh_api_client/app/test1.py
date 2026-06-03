import httpx

CLIENT_ID = "UJQ1RQI4FDD4R86FID7CTKLP1CC5RL310FKI6T9QORGP1LPQP9C78C5TLM2AGA0R"
CLIENT_SECRET = "IUERC7DS2VDBB7F57CS6PEIL672C9U5P49HFTF43TDC114K32S9H9N56UH9J18UU"

def get_app_token():
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
    }

    response = httpx.post(url="https://api.hh.ru/token", data=data, timeout=3)

    print(response.status_code)
    print(response.text)


def get_user_token_pair():
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": "authorization_code",
        "grant_type": "authorization_code",
    }


def get_user_auth_code():
    data = {
        "response_type": "authorization_code",
        "client_id": CLIENT_ID,
        "redirect_uri": "http://localhost:8000/callback"
    }
    headers = {
        "User-Agent": "MyApp/1.0 (antares_hh)",
    }

    response = httpx.get(url=f"https://hh.ru/oauth/authorize?response_type={data["response_type"]}&client_id={data['client_id']}", headers=headers)
    with open("request.txt", "w") as file:
        for key, val in response.__dict__.items():
            file.write(f"[{key}]\n")
            file.write(f"{val}\n")

get_user_auth_code()
