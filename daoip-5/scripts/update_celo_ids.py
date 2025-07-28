
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
        
        # Update grant applications
        if 'grantApplications' in data:
            for app in data['grantApplications']:
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
                    # Extract the actual project ID (assuming it's currently just a number or simple string)
                    if not old_project_id.startswith('celo:42220:'):
                        # Remove any existing prefixes and use the last part
                        project_id_parts = old_project_id.split(':')
                        actual_id = project_id_parts[-1]
                        new_project_id = f"celo:42220:{actual_id}"
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
    
    # Define the grant pool ID mapping based on the grantsPoolURI.json
    grant_pool_id_mapping = {
        "1": "daoip5:celo-org:grantPool:1",
        "2": "daoip5:celo-org:grantPool:2", 
        "3": "daoip5:celo-org:grantPool:3",
        "18": "daoip5:celo-org:grantPool:18",
        "22": "daoip5:celo-org:grantPool:22"
    }
    
    # Files to update
    files_to_update = [
        "../json/celo/agoraForestDAO_round_application_uri.json",
        "../json/celo/bio_pathfinders_application_uri.json",
        "../json/celo/real_world_builders_application_uri.json",
        "../json/celo/regen_citizens_genesis_application_uri.json",
        "../json/celo/regen_coordination_genesis_application_uri.json"
    ]
    
    print("🔄 Starting Celo ID updates...")
    print(f"Grant pool ID mappings: {grant_pool_id_mapping}")
    print()
    
    for file_path in files_to_update:
        if os.path.exists(file_path):
            update_application_ids(file_path, grant_pool_id_mapping)
        else:
            print(f"⚠️  File not found: {file_path}")
        print()
    
    print("✅ Celo ID update process completed!")

if __name__ == "__main__":
    main()
