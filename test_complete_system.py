#!/usr/bin/env python3
"""
Complete System Integration Test
Tests the entire C.A.R.E. system end-to-end
"""

import requests
import json
import time
import pandas as pd
import os
from multiprocessing import Process
import subprocess
import sys

def test_api_connection():
    """Test if API is running and accessible."""
    print("🔌 Testing API connection...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running and accessible")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API - make sure it's running on port 8000")
        return False
    except Exception as e:
        print(f"❌ API connection error: {e}")
        return False

def test_upload_endpoint():
    """Test the upload endpoint with our test data."""
    print("📤 Testing upload endpoint...")
    
    try:
        # Use the test file we created earlier
        test_file_path = "data/test_upload.csv"
        if not os.path.exists(test_file_path):
            print("❌ Test file not found. Creating one...")
            # Create test file from training data
            df = pd.read_csv("data/train.csv").head(5)
            df.to_csv(test_file_path, index=False)
        
        # Upload file
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post("http://localhost:8000/upload", files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Upload endpoint works!")
            print(f"   - Customers analyzed: {data['summary']['total_customers']}")
            print(f"   - Churn rate: {data['summary']['churn_rate']}%")
            print(f"   - Business plan generated: {len(data['business_plan']['strategic_priorities'])} priorities")
            print(f"   - Action items: {len(data['business_plan']['action_plan'])}")
            return data
        else:
            print(f"❌ Upload failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Upload test error: {e}")
        return None

def test_model_info():
    """Test model info endpoint."""
    print("📊 Testing model info endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/model-info", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Model info endpoint works!")
            print(f"   - XGBoost: {data['models_loaded']['xgboost']}")
            print(f"   - Random Forest: {data['models_loaded']['random_forest']}")
            print(f"   - CatBoost: {data['models_loaded']['catboost']}")
            print(f"   - Logistic Regression: {data['models_loaded']['logistic_regression']}")
            print(f"   - Total features: {data['total_features']}")
            return True
        else:
            print(f"❌ Model info failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Model info error: {e}")
        return False

def test_frontend_files():
    """Verify frontend files exist and have correct structure."""
    print("🎨 Testing frontend files...")
    
    frontend_files = {
        "index.html": "frontend/index.html",
        "style.css": "frontend/css/style.css", 
        "app.js": "frontend/js/app.js",
        "README.md": "frontend/README.md"
    }
    
    all_good = True
    for name, path in frontend_files.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✅ {name} exists ({size:,} bytes)")
        else:
            print(f"❌ {name} missing: {path}")
            all_good = False
    
    return all_good

def test_business_plan_quality():
    """Test business plan generation quality."""
    print("🎯 Testing business plan quality...")
    
    try:
        # Import business plan generator
        from model.reasons import compute_top_reasons_with_loaded_models
        from model.business_plan import generate_business_plan
        
        # Get top reasons
        top_reasons = compute_top_reasons_with_loaded_models(top_n=5)
        
        # Sample summary
        customer_summary = {
            'total_customers': 100,
            'churn_rate': 0.25,
            'customers_at_risk': 25,
            'high_risk_customers': 15,
            'medium_risk_customers': 8,
            'low_risk_customers': 77
        }
        
        # Generate business plan
        business_plan = generate_business_plan(top_reasons, customer_summary)
        
        # Quality checks
        required_sections = [
            'executive_summary', 'strategic_priorities', 
            'action_plan', 'success_metrics', 
            'resource_requirements', 'risk_mitigation'
        ]
        
        missing_sections = [s for s in required_sections if s not in business_plan]
        if missing_sections:
            print(f"❌ Missing business plan sections: {missing_sections}")
            return False
        
        # Check priorities
        priorities = business_plan.get('strategic_priorities', [])
        if len(priorities) == 0:
            print("❌ No strategic priorities generated")
            return False
        
        # Check action plan
        actions = business_plan.get('action_plan', [])
        if len(actions) == 0:
            print("❌ No action plan generated")
            return False
        
        print("✅ Business plan quality looks good!")
        print(f"   - Executive summary: {len(business_plan['executive_summary'])} chars")
        print(f"   - Strategic priorities: {len(priorities)}")
        print(f"   - Action items: {len(actions)}")
        print(f"   - Success metrics: {len(business_plan['success_metrics'])}")
        print(f"   - Risk mitigations: {len(business_plan['risk_mitigation'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Business plan quality test failed: {e}")
        return False

def generate_system_report():
    """Generate final system report."""
    print("\n" + "="*60)
    print("🎉 C.A.R.E. SYSTEM INTEGRATION REPORT")
    print("="*60)
    
    # Test all components
    results = {
        "API Connection": test_api_connection(),
        "Upload Endpoint": test_upload_endpoint() is not None,
        "Model Info": test_model_info(),
        "Frontend Files": test_frontend_files(),
        "Business Plan Quality": test_business_plan_quality()
    }
    
    print("\n📊 FINAL RESULTS:")
    print("-" * 30)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if not passed:
            all_passed = False
    
    print("-" * 30)
    
    if all_passed:
        print("\n🚀 ALL TESTS PASSED!")
        print("\n📋 NEXT STEPS:")
        print("1. Start API server: python api/main.py")
        print("2. Open frontend: open frontend/index.html")
        print("3. Upload your customer data and get insights!")
        print("\n🎯 Your C.A.R.E. system is ready for production!")
    else:
        print("\n⚠️ SOME TESTS FAILED!")
        print("Check the errors above and fix issues before proceeding.")
    
    print("\n" + "="*60)

def main():
    """Main test function."""
    print("🧪 C.A.R.E. Complete System Integration Test")
    print("="*60)
    print("Testing all components of your Customer Analytics & Retention Engine\n")
    
    generate_system_report()

if __name__ == "__main__":
    main()