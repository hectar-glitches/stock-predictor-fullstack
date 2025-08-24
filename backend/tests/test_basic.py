"""Simple working tests for CI/CD pipeline"""
import sys
import os

# Add the parent directory to the path so we can import from backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_config_import():
    """Test that configuration can be imported"""
    try:
        from config import settings
        assert settings is not None
        assert hasattr(settings, 'port')
        print("✅ Config import test passed")
        return True
    except Exception as e:
        print(f"❌ Config import test failed: {e}")
        return False

def test_app_import():
    """Test that app can be imported"""
    try:
        import app
        assert app.app is not None
        print("✅ App import test passed")
        return True
    except Exception as e:
        print(f"❌ App import test failed: {e}")
        return False

def test_basic_endpoints():
    """Test basic app functionality"""
    try:
        from fastapi.testclient import TestClient
        from app import app as fastapi_app
        
        client = TestClient(fastapi_app)
        
        # Test root endpoint
        response = client.get("/")
        assert response.status_code == 200
        
        print("✅ Basic endpoint test passed")
        return True
    except Exception as e:
        print(f"❌ Basic endpoint test failed: {e}")
        return False

if __name__ == "__main__":
    """Run tests when called directly"""
    print("Running basic tests...")
    
    tests = [
        test_config_import,
        test_app_import, 
        test_basic_endpoints
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
