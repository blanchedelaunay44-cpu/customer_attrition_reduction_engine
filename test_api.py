#!/usr/bin/env python3
"""
Test script for the Churn Prediction API
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health check endpoint."""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running!")
        return False

def test_upload_endpoint():
    """Test the file upload endpoint."""
    print("\nTesting /upload endpoint...")
    try:
        # Upload the test file
        with open('data/test_upload.csv', 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Upload successful!")
            print(f"Message: {data['message']}")
            print(f"Total customers: {data['summary']['total_customers']}")
            print(f"Customers at risk: {data['summary']['customers_at_risk']}")
            print(f"Churn rate: {data['summary']['churn_rate']}%")
            
            print("\nTop 3 reasons for churn:")
            for i, reason in enumerate(data['top_reasons'][:3], 1):
                print(f"{i}. {reason['feature']} (importance: {reason['importance']:.3f})")
                print(f"   Action: {reason['suggested_action']}")
            
            print("\nSample predictions:")
            for i, pred in enumerate(data['predictions'][:3], 1):
                print(f"{i}. {pred['customer_id']}: {pred['churn_probability']:.3f} ({pred['risk_level']} risk)")
            
        else:
            print(f"Error: {response.text}")
        
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running!")
        return False

def test_model_info():
    """Test the model info endpoint."""
    print("\nTesting /model-info endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/model-info")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running!")
        return False

if __name__ == "__main__":
    print("🧪 Testing Churn Prediction API")
    print("=" * 50)
    
    # Run tests
    health_ok = test_health_endpoint()
    if not health_ok:
        print("\n❌ Please start the API server first:")
        print("   python api/main.py")
        print("   or")
        print("   uvicorn api.main:app --reload")
        exit(1)
    
    model_info_ok = test_model_info()
    upload_ok = test_upload_endpoint()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Health Check: {'PASSED' if health_ok else 'FAILED'}")
    print(f"✅ Model Info: {'PASSED' if model_info_ok else 'FAILED'}")
    print(f"✅ File Upload: {'PASSED' if upload_ok else 'FAILED'}")
    
    if all([health_ok, model_info_ok, upload_ok]):
        print("\n🎉 All tests passed! API is ready for frontend integration.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")