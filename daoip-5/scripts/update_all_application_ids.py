
#!/usr/bin/env python3
"""
Script to update application IDs across all grant systems to follow the correct DAOIP-5 format:
daoip-5:<Grant System Name>:grantPool:<Grant Pool ID>:grantApplication:<Application ID>
"""

import json
import os
from pathlib import Path

def extract_pool_id_from_grant_pool_id(grant_pool_id):
    """Extract the pool ID from various grantPoolId formats."""
    if not grant_pool_id:
        return "unknown"
    
    # Handle different formats
    if grant_pool_id.startswith('daoip5:'):
        # Format: daoip5:system:grantPool:X
        parts = grant_pool_id.split(':')
        if len(parts) >= 4 and parts[2] == 'grantPool':
            return parts[3]
        else:
            return parts[-1]  # fallback to last part
    elif ':' in grant_pool_id:
        # Format like "dao-drops-dorgtech:round_1"
        return grant_pool_id.split(':')[-1]
    else:
        # Simple format
        return grant_pool_id

def get_grant_system_name(file_path):
    """Extract grant system name from file path."""
    path_parts = Path(file_path).parts
    
    # Find the parent directory of the JSON file
    for i, part in enumerate(path_parts):
        if part == 'json' and i + 1 < len(path_parts):
            system_name = path_parts[i + 1]
            
            # Handle special cases
            if system_name == 'dao-drops-dorgtech':
                return 'dao-drops-dorgtech'
            elif system_name == 'arbitrumfoundation':
                return 'arbitrum-foundation'
            elif system_name == 'octant-golemfoundation':
                return 'octant-golem-foundation'
            else:
                return system_name
    
    return "unknown-system"

def update_application_ids_in_file(file_path):
    """Update application IDs in a single file."""
    print(f"Processing: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated = False
        grant_system_name = get_grant_system_name(file_path)
        
        # Process applications in all grant pools
        if 'grantPools' in data and isinstance(data['grantPools'], list):
            for pool in data['grantPools']:
                if 'applications' in pool:
                    for app in pool['applications']:
                        if 'id' in app and 'grantPoolId' in app:
                            old_app_id = app['id']
                            grant_pool_id = app['grantPoolId']
                            
                            # Extract pool ID
                            pool_id = extract_pool_id_from_grant_pool_id(grant_pool_id)
                            
                            # Create the correct format
                            expected_format = f"daoip-5:{grant_system_name}:grantPool:{pool_id}:grantApplication:"
                            
                            # Check if already in correct format
                            if not old_app_id.startswith(expected_format):
                                # Extract application ID
                                if old_app_id.startswith('daoip5:'):
                                    # Extract from existing daoip5 format
                                    parts = old_app_id.split(':')
                                    if 'grantApplication' in parts:
                                        app_id_index = parts.index('grantApplication') + 1
                                        if app_id_index < len(parts):
                                            app_id = parts[app_id_index]
                                        else:
                                            app_id = parts[-1]
                                    else:
                                        app_id = parts[-1]
                                elif old_app_id.startswith('daoip-5:'):
                                    # Already has daoip-5 prefix
                                    app_id = old_app_id.split(':')[-1]
                                else:
                                    # Simple numeric or string ID
                                    app_id = old_app_id
                                
                                # Create new application ID
                                new_app_id = f"daoip-5:{grant_system_name}:grantPool:{pool_id}:grantApplication:{app_id}"
                                app['id'] = new_app_id
                                updated = True
                                print(f"  Updated: {old_app_id} -> {new_app_id}")
        
        if updated:
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"  ✅ Updated {file_path}")
        else:
            print(f"  ℹ️  No updates needed for {file_path}")
            
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")

def main():
    """Main function to update application IDs across all grant systems."""
    
    # Get the script directory and build correct paths
    script_dir = Path(__file__).parent
    json_base_dir = script_dir.parent / "json"
    
    # Define target files
    target_files = [
        # ArbitrumFoundation
        "arbitrumfoundation/stip_1_applications_uri.json",
        
        # CLRFund
        "clrfund/round_9_applications_uri.json",
        
        # DAO Drops
        "dao-drops-dorgtech/round_1_applications_uri.json",
    ]
    
    # Add all Optimism files
    optimism_dir = json_base_dir / "optimism"
    if optimism_dir.exists():
        for file_path in optimism_dir.glob("*_applications_uri.json"):
            relative_path = file_path.relative_to(json_base_dir)
            target_files.append(str(relative_path))
    
    # Add all Stellar files  
    stellar_dir = json_base_dir / "stellar"
    if stellar_dir.exists():
        for file_path in stellar_dir.glob("*_applications_uri.json"):
            relative_path = file_path.relative_to(json_base_dir)
            target_files.append(str(relative_path))
    
    print("🔄 Starting application ID format updates...")
    print(f"Target format: daoip-5:<Grant System Name>:grantPool:<Grant Pool ID>:grantApplication:<Application ID>")
    print()
    
    for relative_file_path in sorted(target_files):
        file_path = json_base_dir / relative_file_path
        if file_path.exists():
            update_application_ids_in_file(file_path)
        else:
            print(f"⚠️  File not found: {file_path}")
        print()
    
    print("✅ Application ID format update process completed!")

if __name__ == "__main__":
    main()
