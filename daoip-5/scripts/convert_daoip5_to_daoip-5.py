
#!/usr/bin/env python3
"""
Script to convert all 'daoip5:' prefixes to 'daoip-5:' in ID fields across all JSON files
in the daoip-5/json directory and its subdirectories.
"""

import json
import os
import re
from pathlib import Path

def update_id_field(value):
    """Convert daoip5: to daoip-5: in a string value."""
    if isinstance(value, str) and value.startswith('daoip5:'):
        return value.replace('daoip5:', 'daoip-5:', 1)
    return value

def process_json_object(obj):
    """Recursively process a JSON object to update ID fields."""
    if isinstance(obj, dict):
        updated_obj = {}
        for key, value in obj.items():
            # Update ID fields (id, grantPoolId, projectId, etc.)
            if key.lower().endswith('id') or key.lower() == 'id':
                updated_obj[key] = update_id_field(value)
            else:
                updated_obj[key] = process_json_object(value)
        return updated_obj
    elif isinstance(obj, list):
        return [process_json_object(item) for item in obj]
    else:
        return obj

def process_file(file_path):
    """Process a single JSON file."""
    print(f"Processing: {file_path}")
    
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Store original data for comparison
        original_data = json.dumps(data, sort_keys=True)
        
        # Process the data
        updated_data = process_json_object(data)
        
        # Check if changes were made
        new_data = json.dumps(updated_data, sort_keys=True)
        if original_data != new_data:
            # Create backup
            backup_path = file_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            # Write updated data
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, indent=4, ensure_ascii=False)
            
            print(f"  ✅ Updated {os.path.basename(file_path)} (backup created)")
            return True
        else:
            print(f"  ℹ️  No changes needed for {os.path.basename(file_path)}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all JSON files."""
    # Get the script directory and build correct paths
    script_dir = Path(__file__).parent
    json_base_dir = script_dir.parent / "json"
    
    if not json_base_dir.exists():
        print(f"❌ Error: Directory {json_base_dir} does not exist")
        return
    
    print("🔄 Converting 'daoip5:' to 'daoip-5:' in all ID fields...")
    print(f"📁 Scanning directory: {json_base_dir}")
    print()
    
    # Find all JSON files recursively
    json_files = list(json_base_dir.rglob("*.json"))
    
    if not json_files:
        print("⚠️  No JSON files found")
        return
    
    print(f"📄 Found {len(json_files)} JSON files")
    print()
    
    updated_count = 0
    
    # Process each file
    for file_path in sorted(json_files):
        if process_file(file_path):
            updated_count += 1
        print()
    
    print(f"✅ Conversion completed!")
    print(f"📊 Summary:")
    print(f"   Total files processed: {len(json_files)}")
    print(f"   Files updated: {updated_count}")
    print(f"   Files unchanged: {len(json_files) - updated_count}")
    
    if updated_count > 0:
        print(f"\n💾 Backup files created with .backup extension")

if __name__ == "__main__":
    main()
