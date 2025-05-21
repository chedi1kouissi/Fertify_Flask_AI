import base64
import requests
import os
import sys
import json

def test_disease_api_base64(image_path):
    """Test the disease prediction API with a base64 encoded image"""
    print(f"\n===== TESTING DISEASE API WITH BASE64 IMAGE: {image_path} =====")
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at path: {image_path}")
        return
    
    try:
        # Read image file and convert to base64
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
            base64_encoded = base64.b64encode(img_data).decode('utf-8')
            
        print(f"Successfully encoded image to base64, length: {len(base64_encoded)} chars")
        
        # Create the data payload
        data = {
            'image_base64': base64_encoded
        }
        
        # Make the request
        print("Sending base64 encoded image to API...")
        response = requests.post(
            "http://localhost:5002/api/predict_disease_base64",
            json=data,
            timeout=60,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Success! Response:")
            print(response.json().get('prediction', 'No prediction returned'))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error in API request: {e}")

def main():
    print("=" * 60)
    print("DISEASE API BASE64 IMAGE TEST")
    print("=" * 60)
    print("This test sends a base64-encoded image to test the API directly")
    
    if len(sys.argv) < 2:
        print("Please provide the path to an image file as an argument.")
        print("Example: python direct_disease_test.py test_leaf.jpg")
        return
    
    image_path = sys.argv[1]
    test_disease_api_base64(image_path)
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main() 