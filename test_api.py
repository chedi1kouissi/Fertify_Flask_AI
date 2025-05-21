import requests
import json
import sys
import time

def test_health_checks():
    """Test the health check endpoints for both services"""
    print("\n===== TESTING HEALTH ENDPOINTS =====")
    
    # Test fertilizer health
    try:
        print("\nTesting Fertilizer Health...")
        resp = requests.get("http://localhost:5001/health", timeout=5)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            print(json.dumps(resp.json(), indent=2))
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Error connecting to fertilizer service: {e}")
    
    # Test disease health
    try:
        print("\nTesting Disease Health...")
        resp = requests.get("http://localhost:5002/health", timeout=5)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            print(json.dumps(resp.json(), indent=2))
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Error connecting to disease service: {e}")

def test_fertilizer_api():
    """Test the fertilizer prediction API"""
    print("\n===== TESTING FERTILIZER API =====")
    
    # Sample data
    data = {
        "pH": 6.5,
        "Nitrogen": 120,
        "Phosphorus": 40,
        "Potassium": 80,
        "temperature": 25,
        "humidity": 65,
        "moisture": 40,
        "territory_type": "Sandy",
        "crop_type": "Rice"
    }
    
    # Test fertilizer API
    try:
        print("\nSending test request to fertilizer API...")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        resp = requests.post(
            "http://localhost:5001/api/predict_fertilizer", 
            json=data,
            timeout=10
        )
        
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Response: {json.dumps(resp.json(), indent=2)}")
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Error calling fertilizer API: {e}")

def test_connectivity():
    """Test basic connectivity to both services"""
    print("\n===== TESTING BASIC CONNECTIVITY =====")
    
    # Test fertilizer connectivity
    try:
        print("\nConnecting to Fertilizer Service...")
        resp = requests.get("http://localhost:5001/", timeout=5)
        print(f"Status Code: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error connecting to fertilizer service: {e}")
    
    # Test disease connectivity
    try:
        print("\nConnecting to Disease Service...")
        resp = requests.get("http://localhost:5002/", timeout=5)
        print(f"Status Code: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error connecting to disease service: {e}")

def main():
    print("=" * 60)
    print("API TESTING SCRIPT")
    print("=" * 60)
    print("This script will test connectivity to both services")
    print("Make sure both services are running using start_services.bat")
    print("=" * 60)
    
    # Test basic connectivity
    test_connectivity()
    
    # Wait a moment
    time.sleep(1)
    
    # Test health endpoints
    test_health_checks()
    
    # Wait a moment
    time.sleep(1)
    
    # Test fertilizer API
    test_fertilizer_api()
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main() 