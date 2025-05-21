import requests
import os
import sys

def test_disease_api_with_image(image_path):
    """Test the disease prediction API with an actual image file"""
    print(f"\n===== TESTING DISEASE API WITH IMAGE: {image_path} =====")
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at path: {image_path}")
        return
    
    # Open the image file
    try:
        # Create multipart form with the file
        with open(image_path, 'rb') as img_file:
            files = {'image': (os.path.basename(image_path), img_file, 'image/jpeg')}
            
            print(f"Sending image {os.path.basename(image_path)} to disease API...")
            
            # Make the POST request to the API
            response = requests.post(
                "http://localhost:5002/api/predict_disease",
                files=files,
                timeout=60
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
    print("DISEASE API IMAGE UPLOAD TEST")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("Please provide the path to an image file as an argument.")
        print("Example: python test_image_upload.py test_leaf.jpg")
        return
    
    image_path = sys.argv[1]
    test_disease_api_with_image(image_path)
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main() 