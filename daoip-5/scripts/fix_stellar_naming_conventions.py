
#!/usr/bin/env python3
"""
Script to fix naming conventions in Stellar JSON files.
Changes scf-X to scf_X in names, IDs, and other relevant fields.
"""

import json
import os
import sys
from pathlib import Path
import re

def fix_naming_conventions(data):
    """
    Recursively fix naming conventions in JSON data.
    Replace scf-X with scf_X in relevant fields.
    """
    if isinstance(data, dict):
        fixed_data = {}
        for key, value in data.items():
            # Fix the value
            if isinstance(value, str):
                # Replace scf-X with scf_X in string values
                fixed_value = re.sub(r'scf-(\d+)', r'scf_\1', value)
                fixed_data[key] = fixed_value
            else:
                fixed_data[key] = fix_naming_conventions(value)
        return fixed_data
    elif isinstance(data, list):
        return [fix_naming_conventions(item) for item in data]
    else:
        return data

def process_stellar_files():
    """Process all JSON files in the stellar directory."""
    script_dir = Path(__file__).parent
    stellar_dir = script_dir.parent / 'json' / 'stellar'
    
    if not stellar_dir.exists():
        print(f"❌ Error: Stellar directory not found: {stellar_dir}")
        return
    
    processed_files = 0
    updated_files = 0
    
    # Process all JSON files in the stellar directory
    for json_file in stellar_dir.glob('*.json'):
        print(f"Processing: {json_file}")
        
        try:
            # Read the original file
            with open(json_file, 'r', encoding='utf-8') as f:
                original_data = json.load(f)
            
            # Fix naming conventions
            fixed_data = fix_naming_conventions(original_data)
            
            # Check if changes were made
            original_json = json.dumps(original_data, sort_keys=True)
            fixed_json = json.dumps(fixed_data, sort_keys=True)
            
            if original_json != fixed_json:
                # Create backup
                backup_path = str(json_file) + '.naming_backup'
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(original_data, f, indent=4, ensure_ascii=False)
                
                # Write the fixed data
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(fixed_data, f, indent=4, ensure_ascii=False)
                
                print(f"  ✅ Updated: {json_file.name}")
                updated_files += 1
            else:
                print(f"  ℹ️  No changes needed: {json_file.name}")
            
            processed_files += 1
            
        except Exception as e:
            print(f"  ❌ Error processing {json_file}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   Total files processed: {processed_files}")
    print(f"   Files updated: {updated_files}")
    print(f"   Files unchanged: {processed_files - updated_files}")

if __name__ == "__main__":
    process_stellar_files()
