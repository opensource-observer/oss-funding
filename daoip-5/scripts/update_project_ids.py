
#!/usr/bin/env python3
"""
DAOIP-5 Project ID Update Script

This script updates all project IDs to the standardized DAOIP-5 format:
- Project IDs: daoip5:<grantSystemName>:project:<projectID>
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


def format_project_id(grant_system_name, original_id):
    """Convert project ID to standardized format."""
    if not original_id or original_id.startswith('daoip5:'):
        return original_id  # Already in correct format or empty
    return f"daoip5:{grant_system_name}:project:{original_id}"


def update_applications_file(file_path, grant_system_name):
    """Update applications JSON file with standardized project IDs."""
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
            # Update applications
            applications = pool.get('applications', [])
            for app in applications:
                # Update project ID
                if 'projectId' in app:
                    old_project_id = app['projectId']
                    new_project_id = format_project_id(grant_system_name, old_project_id)
                    if old_project_id != new_project_id:
                        app['projectId'] = new_project_id
                        changes_made = True
                        print(f"    ✅ Updated project ID: {old_project_id} → {new_project_id}")
        
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
        
        # Skip grants_pool.json as it doesn't contain project IDs
        if json_file.name == 'grants_pool.json':
            continue
            
        files_processed += 1
        
        # Process applications files
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
    
    print("🎯 DAOIP-5 Project ID Update")
    print("=" * 50)
    print("Converting Project IDs to standardized format:")
    print("• Project IDs: daoip5:<grantSystemName>:project:<projectID>")
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
    print(f"🎉 Project ID Update Complete!")
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
