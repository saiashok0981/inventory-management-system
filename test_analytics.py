#!/usr/bin/env python3
"""
Test script to verify analytics dashboard implementation
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_analytics_router_import():
    """Test if analytics router imports successfully"""
    try:
        from routers import analytics
        print("✓ Analytics router imported successfully")
        print(f"  - Router prefix: {analytics.router.prefix}")
        print(f"  - Routes: {len([r for r in analytics.router.routes])}")
        return True
    except Exception as e:
        print(f"✗ Failed to import analytics router: {e}")
        return False

def test_main_app_import():
    """Test if main app imports successfully"""
    try:
        import main
        print("✓ Main application imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import main application: {e}")
        return False

def test_frontend_files_exist():
    """Test if frontend files exist"""
    files_to_check = [
        "frontend/analytics-dashboard.html",
        "frontend/css/analytics-dashboard.css"
    ]
    
    all_exist = True
    for file in files_to_check:
        file_path = project_root / file
        if file_path.exists():
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} missing")
            all_exist = False
    
    return all_exist

def main():
    print("=" * 50)
    print("Analytics Dashboard Implementation Test")
    print("=" * 50)
    print()
    
    tests = [
        ("Analytics Router Import", test_analytics_router_import),
        ("Main Application Import", test_main_app_import),
        ("Frontend Files", test_frontend_files_exist)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Testing: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test error: {e}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("=" * 50)
    print("Test Summary")
    print("=" * 50)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed! Analytics dashboard is ready.")
        return 0
    else:
        print("\n✗ Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
