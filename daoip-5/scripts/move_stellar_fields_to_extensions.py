
#!/usr/bin/env python3
"""
Stellar DAOIP-5 Field Migration Script

This script removes the title field and moves specific fields to extensions
with the org.stellar.communityfund prefix for Stellar applications.
"""

import json
import os
import sys
import shutil
from typing import Dict, List, Any


class StellarFieldMigrator:
    def __init__(self, json_data_dir: str):
        self.json_data_dir = json_data_dir
        self.processed_files = []
        self.backups_created = []
        
        # Fields to move to extensions with org.stellar.communityfund prefix
        self.fields_to_move = {
            "fundsPaid",
            "mostRecentPaymentDate", 
            "latestTranche",
            "awardType",
            "category"
        }
        
        # Fields to remove completely
        self.fields_to_remove = {
            "title"
        }
    
    def create_backup(self, file_path: str) -> str:
        """Create a backup of the original file."""
        backup_path = file_path + '.field_migration_backup'
        shutil.copy2(file_path, backup_path)
        self.backups_created.append(backup_path)
        return backup_path
    
    def migrate_application_fields(self, application: Dict) -> tuple[Dict, bool]:
        """Migrate fields in a single application and return (updated_app, was_modified)."""
        updated_app = application.copy()
        was_modified = False
        
        # Get existing extensions or create new one
        extensions = updated_app.get('extensions', {})
        
        # Remove title field
        if 'title' in updated_app:
            del updated_app['title']
            was_modified = True
        
        # Move specified fields to extensions
        for field in self.fields_to_move:
            if field in updated_app:
                value = updated_app.pop(field)
                extensions[f'org.stellar.communityfund.{field}'] = value
                was_modified = True
        
        # Update extensions if we added anything
        if extensions:
            updated_app['extensions'] = extensions
        
        return updated_app, was_modified
    
    def process_file(self, file_path: str) -> bool:
        """Process a single JSON file."""
        try:
            # Create backup
            backup_path = self.create_backup(file_path)
            
            # Load JSON data
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            modified_count = 0
            total_applications = 0
            
            # Process applications in all grant pools
            for pool in data.get('grantPools', []):
                for i, app in enumerate(pool.get('applications', [])):
                    total_applications += 1
                    updated_app, was_modified = self.migrate_application_fields(app)
                    
                    if was_modified:
                        pool['applications'][i] = updated_app
                        modified_count += 1
            
            # Only save if modifications were made
            if modified_count > 0:
                # Save updated file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                filename = os.path.basename(file_path)
                print(f"✅ {filename}: {modified_count}/{total_applications} applications migrated")
                self.processed_files.append(filename)
                return True
            else:
                filename = os.path.basename(file_path)
                print(f"ℹ️  {filename}: No fields to migrate")
                return False
                
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False
    
    def process_all_files(self) -> None:
        """Process all JSON files in the stellar directory."""
        print(f"🚀 Starting Stellar field migration")
        print(f"   Removing title field and moving specified fields to extensions...")
        print(f"   Target fields: {', '.join(self.fields_to_move)}")
        print(f"   Fields to remove: {', '.join(self.fields_to_remove)}")
        
        # Find all application URI files
        json_files = [f for f in os.listdir(self.json_data_dir) 
                     if f.endswith('_applications_uri.json')]
        
        if not json_files:
            print(f"⚠️  No application URI files found in {self.json_data_dir}")
            return
        
        print(f"   Found {len(json_files)} application files to process")
        
        # Process each file
        for filename in sorted(json_files):
            file_path = os.path.join(self.json_data_dir, filename)
            self.process_file(file_path)
        
        # Summary
        print(f"\n📊 Field Migration Summary:")
        print(f"   Files processed: {len(self.processed_files)}")
        print(f"   Backups created: {len(self.backups_created)}")
        
        if self.processed_files:
            print(f"   Modified files: {', '.join(self.processed_files[:5])}")
            if len(self.processed_files) > 5:
                print(f"   ... and {len(self.processed_files) - 5} more")
        
        print(f"\n💡 Migration completed. Fields moved to extensions with 'org.stellar.communityfund' prefix.")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_data_dir = os.path.join(script_dir, '..', 'json', 'stellar')
    
    # Verify directory exists
    if not os.path.exists(json_data_dir):
        print(f"❌ Error: JSON data directory not found: {json_data_dir}")
        sys.exit(1)
    
    migrator = StellarFieldMigrator(json_data_dir)
    migrator.process_all_files()


if __name__ == "__main__":
    main()
