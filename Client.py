import requests
import time
import threading
from api import start_api  # Import from server.py

BASE_URL = "http://localhost:5000"
EMAIL = "yuri@gmail.com"
PASSWORD = "SecurePass123"

def check_api():
    try:
        response = requests.get(BASE_URL, timeout=2)
        return response.status_code == 200
    except requests.ConnectionError:
        return False

def login(email, password):
    response = requests.post(f"{BASE_URL}/login", json={"email": email, "password": password})
    if response.status_code == 200:
        print("✅ Login successful!")
        return response.json().get("access_token")
    print("❌ Login failed:", response.json().get("error"))
    return None

def upload_csv(token, file_path):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        with open(file_path, "rb") as file:
            files = {"file": file}
            response = requests.post(f"{BASE_URL}/upload_csv", headers=headers, files=files)
            print(response.json())
    except FileNotFoundError:
        print("❌ File not found. Please check the path and try again.")

def view_transactions(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/transactions", headers=headers)
    transactions = response.json()
    if transactions:
        for tx in transactions:
            print(tx)
    else:
        print("No transactions found.")

def main():    
    if not check_api():
        print("🚀 Starting the API...")
        api_thread = threading.Thread(target=start_api)
        api_thread.daemon = True
        api_thread.start()

        # Retry logic (wait up to 10 seconds)
        for _ in range(10):
            if check_api():
                print("✅ API is up and running!")
                break
            time.sleep(1)
        else:
            print("❌ API failed to start.")
            return
        

    token = login(EMAIL, PASSWORD)
    if not token:
        return

    while True:
        print("\nChoose an action:")
        print("1. Upload CSV")
        print("2. View Transactions")
        print("3. Exit")

        choice = input("Enter your choice (1/2/3): ")

        if choice == "1":
            file_path = input("Enter the CSV file path: ")
            upload_csv(token, file_path)
        elif choice == "2":
            view_transactions(token)
        elif choice == "3":
            print("👋 Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
