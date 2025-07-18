
#!/usr/bin/env python3
"""
DAOIP-5 Schema Compliance Script

This script moves non-standard fields to the extensions field according to 
the DAOIP-5 specification to ensure full schema compliance.
"""

import json
import os
import sys
import shutil
from typing import Dict, List, Any, Set


class SchemaComplianceProcessor:
    def __init__(self, json_data_dir: str):
        self.json_data_dir = json_data_dir
        self.processed_files = []
        self.backups_created = []
        
        # Standard DAOIP-5 fields for GrantApplication according to the schema
        self.standard_application_fields = {
            "type", "id", "grantPoolsURI", "grantPoolId", "grantPoolName",
            "projectsURI", "projectId", "projectName", "createdAt", "contentURI",
            "discussionsTo", "licenseURI", "isInactive", "applicationCompletionRate",
            "socials", "fundsAsked", "fundsAskedInUSD", "fundsApproved", 
            "fundsApprovedInUSD", "payoutAddress", "status", "payouts", "extensions"
        }
        
        # Additional commonly accepted fields that should remain in core
        self.accepted_core_fields = {
            "@context", "name", "type", "description", "title",
            "fundsPaid", "mostRecentPaymentDate", "latestTranche", 
            "awardType", "category", "completionPercentage"
        }
        
        # All allowed core fields
        self.all_core_fields = self.standard_application_fields.union(self.accepted_core_fields)
    
    def create_backup(self, file_path: str) -> str:
        """Create a backup of the original file."""
        backup_path = file_path + '.schema_backup'
        shutil.copy2(file_path, backup_path)
        self.backups_created.append(backup_path)
        return backup_path
    
    def identify_non_standard_fields(self, application: Dict) -> Set[str]:
        """Identify fields that should be moved to extensions."""
        application_fields = set(application.keys())
        return application_fields - self.all_core_fields
    
    def move_fields_to_extensions(self, application: Dict) -> Dict:
        """Move non-standard fields to extensions with stellar prefix."""
        non_standard_fields = self.identify_non_standard_fields(application)
        
        if not non_standard_fields:
            return application
        
        # Get existing extensions or create new one
        extensions = application.get('extensions', {})
        
        # Move fields to extensions with stellar prefix
        for field in non_standard_fields:
            value = application.pop(field)
            # Use stellar prefix for ecosystem-specific data
            extensions[f'stellar.{field}'] = value
        
        # Update extensions if we added anything
        if extensions:
            application['extensions'] = extensions
        
        return application
    
    def process_application(self, app: Dict) -> tuple[Dict, bool]:
        """Process a single application and return (updated_app, was_modified)."""
        original_app = json.dumps(app, sort_keys=True)
        
        # Move non-standard fields to extensions
        updated_app = self.move_fields_to_extensions(app.copy())
        
        # Check if changes were made
        new_app = json.dumps(updated_app, sort_keys=True)
        was_modified = original_app != new_app
        
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
                    updated_app, was_modified = self.process_application(app)
                    
                    if was_modified:
                        pool['applications'][i] = updated_app
                        modified_count += 1
            
            # Save updated file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            filename = os.path.basename(file_path)
            if modified_count > 0:
                print(f"✅ {filename}: {modified_count}/{total_applications} applications updated")
                self.processed_files.append(filename)
                return True
            else:
                print(f"ℹ️  {filename}: No schema compliance issues found")
                return False
                
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False
    
    def process_all_files(self) -> None:
        """Process all JSON files in the stellar directory."""
        print(f"🚀 Processing Stellar DAOIP-5 schema compliance")
        print(f"   Moving non-standard fields to extensions...")
        
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
        print(f"\n📊 Schema Compliance Summary:")
        print(f"   Files processed: {len(self.processed_files)}")
        print(f"   Backups created: {len(self.backups_created)}")
        
        if self.processed_files:
            print(f"   Updated files: {', '.join(self.processed_files[:5])}")
            if len(self.processed_files) > 5:
                print(f"   ... and {len(self.processed_files) - 5} more")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_data_dir = os.path.join(script_dir, '..', 'json', 'stellar')
    
    # Verify directory exists
    if not os.path.exists(json_data_dir):
        print(f"❌ Error: JSON data directory not found: {json_data_dir}")
        sys.exit(1)
    
    processor = SchemaComplianceProcessor(json_data_dir)
    processor.process_all_files()


if __name__ == "__main__":
    main()
