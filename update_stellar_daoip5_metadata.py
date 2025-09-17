#!/usr/bin/env python3
"""
Update all Stellar DAOIP-5 files to change name and type
"""

import json
import os
import glob

def update_daoip5_file(file_path):
    """Update a single DAOIP-5 file"""
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if this is a Stellar file that needs updating
        if data.get('name') == 'Stellar' and data.get('type') == 'Foundation':
            # Update name and type
            data['name'] = 'Stellar Community Fund'
            data['type'] = 'Entity'
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Updated {file_path}")
            return True
        else:
            print(f"⏭️ Skipped {file_path} (already updated or different format)")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    """Update all Stellar DAOIP-5 files"""
    stellar_dir = 'daoip-5/json/stellar'
    
    if not os.path.exists(stellar_dir):
        print(f"Directory {stellar_dir} not found")
        return
    
    # Get all JSON files in the stellar directory
    json_files = glob.glob(os.path.join(stellar_dir, '*.json'))
    
    print(f"Found {len(json_files)} JSON files to process...")
    print("=" * 50)
    
    updated_count = 0
    
    for file_path in sorted(json_files):
        file_name = os.path.basename(file_path)
        if update_daoip5_file(file_path):
            updated_count += 1
    
    print("=" * 50)
    print(f"✅ Successfully updated {updated_count} files")
    print(f"📁 Total files processed: {len(json_files)}")
    
    # Verify a few key files
    print("\nVerifying key files:")
    test_files = [
        'grants_pool.json',
        'scf_36_applications_uri.json', 
        'scf_37_applications_uri.json',
        'scf_38_applications_uri.json'
    ]
    
    for test_file in test_files:
        file_path = os.path.join(stellar_dir, test_file)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"  {test_file}: name='{data.get('name')}', type='{data.get('type')}'")
            except Exception as e:
                print(f"  {test_file}: ERROR - {e}")
        else:
            print(f"  {test_file}: FILE NOT FOUND")

if __name__ == "__main__":
    main()