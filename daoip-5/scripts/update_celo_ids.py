
#!/usr/bin/env python3
"""
Script to update IDs in Celo application URI files to follow DAOIP-5 format:
- Grant pool IDs: daoip5:celo-org:grantPool:<ID>
- Project IDs: celo:42220:<projectID>
"""

import json
import os
import re
from pathlib import Path

def update_application_ids(file_path, grant_pool_id_mapping):
    """Update IDs in a single application URI file."""
    print(f"Processing: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated = False
        
        # Update grant applications - look for the correct structure
        if 'grantPools' in data and isinstance(data['grantPools'], list):
            for pool in data['grantPools']:
                if 'applications' in pool:
                    for app in pool['applications']:
                        # Update grantPoolId
                        if 'grantPoolId' in app:
                            old_id = app['grantPoolId']
                            if old_id in grant_pool_id_mapping:
                                app['grantPoolId'] = grant_pool_id_mapping[old_id]
                                updated = True
                                print(f"  Updated grantPoolId: {old_id} -> {app['grantPoolId']}")
                        
                        # Update projectId to celo:42220:<projectID> format
                        if 'projectId' in app:
                            old_project_id = app['projectId']
                            # Check if it's already in the correct format
                            if not old_project_id.startswith('celo:42220:'):
                                # Use the existing project ID (which appears to be a hash)
                                new_project_id = f"celo:42220:{old_project_id}"
                                app['projectId'] = new_project_id
                                updated = True
                                print(f"  Updated projectId: {old_project_id} -> {new_project_id}")
        
        if updated:
            # Write back to file with proper formatting
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"  ✅ Updated {file_path}")
        else:
            print(f"  ℹ️  No updates needed for {file_path}")
            
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")

def main():
    """Main function to update all Celo application URI files."""
    
    # Define the grant pool ID mapping based on the grants_pool.json
    grant_pool_id_mapping = {
        "1": "daoip5:celo-org:grantPool:1",
        "2": "daoip5:celo-org:grantPool:2", 
        "3": "daoip5:celo-org:grantPool:3",
        "18": "daoip5:celo-org:grantPool:18",
        "22": "daoip5:celo-org:grantPool:22"
    }
    
    # Get the script directory and build correct paths
    script_dir = Path(__file__).parent
    celo_json_dir = script_dir.parent / "json" / "celo"
    
    # Files to update - using actual file names
    files_to_update = [
        "agoraForestDAO_round_application_uri.json",
        "bio_pathfinders_application_uri.json", 
        "real_world_builders_application_uri.json",
        "regen_citizens_genesis_application_uri.json",
        "regen_coordination_genesis_application_uri.json"
    ]
    
    print("🔄 Starting Celo ID updates...")
    print(f"Grant pool ID mappings: {grant_pool_id_mapping}")
    print()
    
    for filename in files_to_update:
        file_path = celo_json_dir / filename
        if file_path.exists():
            update_application_ids(file_path, grant_pool_id_mapping)
        else:
            print(f"⚠️  File not found: {file_path}")
        print()
    
    print("✅ Celo ID update process completed!")

if __name__ == "__main__":
    main()
