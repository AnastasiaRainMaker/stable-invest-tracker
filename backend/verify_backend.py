import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def test_backend():
    print("Testing Backend...")
    
    # 1. Create a Stock (KO - Coca Cola is usually stable)
    print("Creating Stock KO...")
    try:
        response = requests.post(f"{BASE_URL}/stocks/", json={"symbol": "KO"})
        if response.status_code != 201:
            print(f"Failed to create stock: {response.content}")
            return
        
        stock_data = response.json()
        print(f"Stock Created: {stock_data['name']} ({stock_data['symbol']})")
        print(f"Price: {stock_data['current_price']}")
        print(f"Stable: {stock_data['is_stable']}")
        
        stock_id = stock_data['id']
        
        # 2. Add to Portfolio
        print("Adding to Portfolio...")
        p_response = requests.post(f"{BASE_URL}/portfolio/", json={
            "stock": stock_id,
            "purchase_price": "50.00",
            "quantity": "10"
        })
        if p_response.status_code != 201:
            print(f"Failed to add portfolio item: {p_response.content}")
        else:
            print("Portfolio Item Added.")
            
        # 3. Check Alerts (Should be empty initially unless price dropped huge)
        print("Checking Alerts...")
        a_response = requests.get(f"{BASE_URL}/alerts/")
        print(f"Alerts found: {len(a_response.json())}")
        
    except Exception as e:
        print(f"Exception during test: {e}")

if __name__ == "__main__":
    # Wait for server to be ready
    time.sleep(2)
    test_backend()
