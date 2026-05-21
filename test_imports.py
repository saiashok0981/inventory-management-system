#!/usr/bin/env python
"""Quick test to validate all module imports."""

import sys
print("Testing module imports...")

try:
    print("✓ Importing routers.projects...")
    from routers import projects
    print("✓ Importing routers.auth...")
    from routers import auth
    print("✓ Importing routers.users...")
    from routers import users
    print("✓ Importing main...")
    import main
    print("\n✅ All imports successful!")
except Exception as e:
    print(f"\n❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
