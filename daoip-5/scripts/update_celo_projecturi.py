
#!/usr/bin/env python3
"""
Update all Celo projectURI files to remove socials and contentURI,
update IDs to DAOIP-5 format, and keep email field.
"""

import json
import os
from pathlib import Path

def update_project_file(file_path):
    """Update a single project JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get project name for the new ID
        project_name = data.get('name', '')
        
        # Update the ID to DAOIP-5 format
        data['id'] = f"daoip5:celo-org:project:{project_name}"
        
        # Remove contentURI if it exists
        if 'contentURI' in data:
            del data['contentURI']
        
        # Remove socials if it exists
        if 'socials' in data:
            del data['socials']
        
        # Keep email field as is
        
        # Write back the updated data
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            f.write('\n    // TODO: Add to OSS-Directory\n')
        
        print(f"✅ Updated {file_path.name}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    """Main function to update all project files."""
    script_dir = Path(__file__).parent
    project_uri_dir = script_dir.parent / "json" / "celo" / "projectURI"
    
    if not project_uri_dir.exists():
        print(f"❌ Directory not found: {project_uri_dir}")
        return
    
    print(f"🔍 Processing files in: {project_uri_dir}")
    
    json_files = list(project_uri_dir.glob("*.json"))
    updated_count = 0
    
    for json_file in json_files:
        if update_project_file(json_file):
            updated_count += 1
    
    print(f"\n✅ Successfully updated {updated_count} out of {len(json_files)} files")

if __name__ == "__main__":
    main()
