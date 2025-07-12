
#!/usr/bin/env python3
"""
DAOIP-5 Critical Issues Fix Script

This script implements Phase 1 critical fixes:
1. Standardize grant_pools → grantPools
2. Fix date formats to ISO8601
3. Convert "Unknown" amounts to null
"""

import json
import os
import sys
import re
from datetime import datetime
from typing import Dict, Any


class CriticalIssuesFixer:
    def __init__(self, system_path: str):
        self.system_path = system_path
        self.system_name = os.path.basename(system_path)
        self.fixes_applied = {
            'schema_fixes': 0,
            'date_fixes': 0,
            'unknown_amount_fixes': 0,
            'files_processed': 0
        }
    
    def fix_date_format(self, date_str: str) -> str:
        """Convert various date formats to ISO8601."""
        if not date_str or date_str == "null":
            return date_str
        
        # Already ISO8601
        if re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', date_str):
            return date_str
        
        # Handle MM/DD/YYYY format
        if re.match(r'^\d{2}/\d{2}/\d{4}', date_str):
            try:
                # Extract just the date part if there's a time component
                date_part = date_str.split('T')[0]
                date_obj = datetime.strptime(date_part, '%m/%d/%Y')
                time_part = 'T00:00:00Z'
                if 'T' in date_str:
                    time_part = 'T' + date_str.split('T')[1]
                fixed_date = date_obj.strftime('%Y-%m-%d') + time_part
                self.fixes_applied['date_fixes'] += 1
                return fixed_date
            except ValueError:
                pass
        
        # Handle YYYY-MM-DD without time
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str + 'T00:00:00Z'
        
        return date_str
    
    def fix_unknown_amounts(self, obj: Any) -> Any:
        """Recursively fix 'Unknown' string amounts to null."""
        if isinstance(obj, dict):
            fixed_obj = {}
            for key, value in obj.items():
                if key == 'amount' and value == "Unknown":
                    fixed_obj[key] = None
                    self.fixes_applied['unknown_amount_fixes'] += 1
                elif key == 'denomination' and value == "Unknown":
                    fixed_obj[key] = None
                    self.fixes_applied['unknown_amount_fixes'] += 1
                else:
                    fixed_obj[key] = self.fix_unknown_amounts(value)
            return fixed_obj
        elif isinstance(obj, list):
            return [self.fix_unknown_amounts(item) for item in obj]
        else:
            return obj
    
    def fix_schema_naming(self, data: Dict) -> Dict:
        """Fix schema naming from grant_pools to grantPools."""
        if 'grant_pools' in data and 'grantPools' not in data:
            data['grantPools'] = data.pop('grant_pools')
            self.fixes_applied['schema_fixes'] += 1
        
        return data
    
    def fix_application_dates(self, app: Dict) -> Dict:
        """Fix date formats in application."""
        date_fields = ['createdAt', 'updatedAt', 'closeDate']
        
        for field in date_fields:
            if field in app and app[field]:
                original_date = app[field]
                fixed_date = self.fix_date_format(original_date)
                if fixed_date != original_date:
                    app[field] = fixed_date
        
        return app
    
    def process_file(self, file_path: str) -> bool:
        """Process a single JSON file and apply fixes."""
        try:
            # Read original file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            original_data = json.dumps(data, sort_keys=True)
            
            # Apply fixes
            # 1. Fix schema naming
            data = self.fix_schema_naming(data)
            
            # 2. Fix unknown amounts
            data = self.fix_unknown_amounts(data)
            
            # 3. Fix date formats
            pools_key = 'grantPools' if 'grantPools' in data else 'grant_pools'
            if pools_key in data:
                for pool in data[pools_key]:
                    if 'applications' in pool:
                        for app in pool['applications']:
                            app = self.fix_application_dates(app)
            
            # Check if changes were made
            new_data = json.dumps(data, sort_keys=True)
            if original_data != new_data:
                # Create backup
                backup_path = file_path + '.backup'
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(json.loads(original_data), f, indent=2, ensure_ascii=False)
                
                # Write fixed file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Fixed: {os.path.basename(file_path)} (backup: {os.path.basename(backup_path)})")
                return True
            else:
                print(f"ℹ️  No fixes needed: {os.path.basename(file_path)}")
                return False
                
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False
    
    def fix_system(self):
        """Fix all JSON files in the grant system."""
        print(f"🔧 Applying critical fixes to: {self.system_name}")
        
        json_files = [f for f in os.listdir(self.system_path) if f.endswith('.json')]
        
        for filename in json_files:
            if filename == 'data_quality_report.json':
                continue  # Skip report files
                
            file_path = os.path.join(self.system_path, filename)
            if self.process_file(file_path):
                self.fixes_applied['files_processed'] += 1
        
        # Print summary
        print(f"\n📊 Fixes Applied to {self.system_name}:")
        print(f"   Files processed: {self.fixes_applied['files_processed']}")
        print(f"   Schema fixes: {self.fixes_applied['schema_fixes']}")
        print(f"   Date fixes: {self.fixes_applied['date_fixes']}")
        print(f"   Unknown amount fixes: {self.fixes_applied['unknown_amount_fixes']}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_critical_issues.py <grant_system_path> [all]")
        print("Examples:")
        print("  python fix_critical_issues.py ../json/arbitrumfoundation")
        print("  python fix_critical_issues.py ../json all  # Fix all systems")
        sys.exit(1)
    
    path_arg = sys.argv[1]
    
    if len(sys.argv) == 3 and sys.argv[2] == 'all':
        # Fix all systems
        json_dir = path_arg
        if not os.path.exists(json_dir):
            print(f"❌ Error: Directory {json_dir} does not exist")
            sys.exit(1)
        
        systems = [d for d in os.listdir(json_dir) if os.path.isdir(os.path.join(json_dir, d))]
        print(f"🚀 Fixing critical issues in {len(systems)} grant systems...")
        
        for system in systems:
            system_path = os.path.join(json_dir, system)
            fixer = CriticalIssuesFixer(system_path)
            fixer.fix_system()
            print()  # Add spacing between systems
        
        print("✅ All systems processed!")
        
    else:
        # Fix single system
        system_path = path_arg
        if not os.path.exists(system_path):
            print(f"❌ Error: Path {system_path} does not exist")
            sys.exit(1)
        
        fixer = CriticalIssuesFixer(system_path)
        fixer.fix_system()


if __name__ == "__main__":
    main()
