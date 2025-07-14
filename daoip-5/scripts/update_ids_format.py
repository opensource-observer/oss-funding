
#!/usr/bin/env python3
"""
DAOIP-5 ID Format Standardization Script

This script converts all IDs to the standardized DAOIP-5 format:
- Application IDs: daoip5:<grantSystemName>:grantApplication:<applicationID>
- Grant Pool IDs: daoip5:<grantSystemName>:grantPool:<ID>
"""

import json
import os
import sys
from pathlib import Path


def create_backup(file_path):
    """Create a backup of the original file."""
    backup_path = f"{file_path}.backup"
    with open(file_path, 'r', encoding='utf-8') as original:
        with open(backup_path, 'w', encoding='utf-8') as backup:
            backup.write(original.read())
    print(f"  📁 Backup created: {backup_path}")


def format_grant_pool_id(grant_system_name, original_id):
    """Convert grant pool ID to standardized format."""
    if original_id.startswith('daoip5:'):
        return original_id  # Already in correct format
    return f"daoip5:{grant_system_name}:grantPool:{original_id}"


def format_application_id(grant_system_name, original_id):
    """Convert application ID to standardized format."""
    if original_id.startswith('daoip5:'):
        return original_id  # Already in correct format
    return f"daoip5:{grant_system_name}:grantApplication:{original_id}"


def update_grant_pools_file(file_path, grant_system_name):
    """Update grant pools JSON file with standardized IDs."""
    print(f"  🔄 Processing grant pools file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create backup
        create_backup(file_path)
        
        changes_made = False
        
        # Update grantPools array
        grant_pools = data.get('grantPools', [])
        for pool in grant_pools:
            if 'id' in pool:
                old_id = pool['id']
                new_id = format_grant_pool_id(grant_system_name, old_id)
                if old_id != new_id:
                    pool['id'] = new_id
                    changes_made = True
                    print(f"    ✅ Updated pool ID: {old_id} → {new_id}")
        
        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"  💾 Saved changes to {file_path}")
        else:
            print(f"  ✨ No changes needed for {file_path}")
            
        return changes_made
        
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False


def update_applications_file(file_path, grant_system_name):
    """Update applications JSON file with standardized IDs."""
    print(f"  🔄 Processing applications file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create backup
        create_backup(file_path)
        
        changes_made = False
        
        # Update grantPools array (supporting both 'grantPools' and 'grant_pools')
        pools_key = 'grantPools' if 'grantPools' in data else 'grant_pools'
        grant_pools = data.get(pools_key, [])
        
        for pool in grant_pools:
            # Update pool ID if present
            if 'id' in pool:
                old_pool_id = pool['id']
                new_pool_id = format_grant_pool_id(grant_system_name, old_pool_id)
                if old_pool_id != new_pool_id:
                    pool['id'] = new_pool_id
                    changes_made = True
                    print(f"    ✅ Updated pool ID: {old_pool_id} → {new_pool_id}")
            
            # Update applications
            applications = pool.get('applications', [])
            for app in applications:
                # Update application ID
                if 'id' in app:
                    old_app_id = app['id']
                    new_app_id = format_application_id(grant_system_name, old_app_id)
                    if old_app_id != new_app_id:
                        app['id'] = new_app_id
                        changes_made = True
                        print(f"    ✅ Updated application ID: {old_app_id} → {new_app_id}")
                
                # Update grantPoolId reference
                if 'grantPoolId' in app:
                    old_ref_id = app['grantPoolId']
                    new_ref_id = format_grant_pool_id(grant_system_name, old_ref_id)
                    if old_ref_id != new_ref_id:
                        app['grantPoolId'] = new_ref_id
                        changes_made = True
                        print(f"    ✅ Updated grantPoolId reference: {old_ref_id} → {new_ref_id}")
        
        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"  💾 Saved changes to {file_path}")
        else:
            print(f"  ✨ No changes needed for {file_path}")
            
        return changes_made
        
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False


def process_grant_system(system_path):
    """Process a single grant system directory."""
    system_name = system_path.name
    print(f"\n🚀 Processing grant system: {system_name}")
    
    total_changes = 0
    files_processed = 0
    
    # Process all JSON files in the system directory
    for json_file in system_path.glob("*.json"):
        if json_file.name.endswith('.backup'):
            continue  # Skip backup files
            
        files_processed += 1
        
        if 'applications' in json_file.name:
            # This is an applications file
            if update_applications_file(json_file, system_name):
                total_changes += 1
        elif json_file.name == 'grants_pool.json':
            # This is a grant pools file
            if update_grant_pools_file(json_file, system_name):
                total_changes += 1
        else:
            # Try to process as applications file (fallback)
            if update_applications_file(json_file, system_name):
                total_changes += 1
    
    print(f"✅ Completed {system_name}: {files_processed} files processed, {total_changes} files modified")
    return total_changes


def main():
    """Main function to process all grant systems."""
    script_dir = Path(__file__).parent
    json_dir = script_dir.parent / "json"
    
    if not json_dir.exists():
        print(f"❌ JSON directory not found: {json_dir}")
        sys.exit(1)
    
    print("🎯 DAOIP-5 ID Format Standardization")
    print("=" * 50)
    print("Converting IDs to standardized format:")
    print("• Application IDs: daoip5:<grantSystemName>:grantApplication:<applicationID>")
    print("• Grant Pool IDs: daoip5:<grantSystemName>:grantPool:<ID>")
    print("=" * 50)
    
    total_systems = 0
    total_changes = 0
    
    # Process each grant system directory
    for system_dir in json_dir.iterdir():
        if system_dir.is_dir() and not system_dir.name.startswith('.'):
            total_systems += 1
            changes = process_grant_system(system_dir)
            total_changes += changes
    
    print("\n" + "=" * 50)
    print(f"🎉 ID Format Standardization Complete!")
    print(f"📊 Summary:")
    print(f"   • Grant systems processed: {total_systems}")
    print(f"   • Files modified: {total_changes}")
    print(f"   • Backup files created for safety")
    print("=" * 50)
    
    if total_changes > 0:
        print("\n💡 Next steps:")
        print("   1. Review the changes in modified files")
        print("   2. Run data quality validation: python3 run_data_quality_check.py validate-all")
        print("   3. Test API endpoints to ensure compatibility")


if __name__ == "__main__":
    main()
