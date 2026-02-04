#!/usr/bin/env python3
"""
Quick test to verify filesystem integration is registered in server.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.server import create_app


def test_server_integration():
    """Test that filesystem integration is registered."""
    print("=== Server Integration Test ===\n")
    
    # Create app
    print("1. Creating FastAPI app...")
    app = create_app()
    print("   ✅ App created\n")
    
    # Check integration manager
    print("2. Checking integration manager...")
    if hasattr(app.state, 'integration_manager') and app.state.integration_manager:
        manager = app.state.integration_manager
        print(f"   ✅ Manager exists\n")
        
        # List all integrations
        print("3. Registered integrations:")
        statuses = manager.get_all_statuses()
        for name, status in statuses.items():
            print(f"   - {name}: {status}")
        print()
        
        # Check filesystem specifically
        print("4. FileSystem integration:")
        fs = manager.get_integration("filesystem")
        if fs:
            print(f"   ✅ Found")
            print(f"   Status: {fs.get_status()}")
            print(f"   Dry-run: {fs.dry_run}")
            print(f"   Protected paths: {len(fs.PROTECTED_PATHS)}")
            print(f"   Warning paths: {len(fs.WARNING_PATHS)}")
        else:
            print("   ❌ Not found")
        print()
    else:
        print("   ❌ Manager not initialized\n")
    
    # Check routes
    print("5. Checking filesystem API routes:")
    filesystem_routes = [
        route for route in app.routes 
        if hasattr(route, 'path') and '/filesystem/' in route.path
    ]
    
    if filesystem_routes:
        print(f"   ✅ Found {len(filesystem_routes)} routes:")
        for route in filesystem_routes:
            print(f"   - {route.methods} {route.path}")
    else:
        print("   ❌ No filesystem routes found")
    
    print("\n✅ Test complete!")


if __name__ == "__main__":
    test_server_integration()
