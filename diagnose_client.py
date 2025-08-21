import requests

SERVER_URL = "http://127.0.0.1:8080/docs"

def main():
    print(f"Attempting to get API docs from {SERVER_URL}...")
    try:
        response = requests.get(SERVER_URL, timeout=10)
        response.raise_for_status()
        
        print("\n--- Success! ---")
        print("Server is a FastAPI app. Response from /docs:")
        # We don't need the full HTML, just knowing we got it is enough.
        print(f"Response length: {len(response.text)}")
        if "FastAPI" in response.text:
            print("Confirmed FastAPI server.")
        else:
            print("Response does not look like FastAPI docs.")

    except requests.exceptions.RequestException as e:
        print(f"\n--- Error ---")
        print(f"Failed to connect to the server at {SERVER_URL}: {e}")

if __name__ == "__main__":
    main()
