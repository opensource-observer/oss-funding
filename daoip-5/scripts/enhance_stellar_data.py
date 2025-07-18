
#!/usr/bin/env python3
"""
Stellar DAOIP-5 Data Enhancement Script

This script processes the raw CSV files and enhances existing JSON files
with additional fields according to DAOIP-5 and DAOIP-5 extension formats.
"""

import csv
import json
import os
import sys
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional
import re


class StellarDataEnhancer:
    def __init__(self, raw_data_dir: str, json_data_dir: str):
        self.raw_data_dir = raw_data_dir
        self.json_data_dir = json_data_dir
        self.enhanced_files = []
        self.backups_created = []
        
        # Field mapping for DAOIP-5 extension fields
        self.field_mapping = {
            'Submission Title': 'title',
            'One-Sentence-Description': 'description',
            'Products & Services': 'productsAndServices',
            'Technical Architecture': 'technicalArchitecture',
            'Success Criteria': 'successCriteria',
            'Website': 'website',
            'Code': 'codeRepository',
            'Video': 'videoURL',
            'Use Soroban?': 'usesSoroban',
            'Go-To-Market Plan': 'goToMarketPlan',
            'Traction Evidence': 'tractionEvidence',
            'Tranche 1 - Deliverables': 'tranche1Deliverables',
            'Tranche 2 - Testnet': 'tranche2Testnet',
            'Tranche 3 - Mainnet': 'tranche3Mainnet',
            'Team Members': 'teamMembers',
            'LinkedIn (from Project)': 'linkedIn',
            'X (from Project)': 'twitter',
            'Discord (from Project)': 'discord',
            'Pitch Deck (from Project)': 'pitchDeck',
            'Status': 'status',
            'Tranche Completion %': 'trancheCompletionPercent',
            'Latest Tranche (from Payments)': 'latestTranche',
            'Total Paid (USD)': 'totalPaidUSD',
            'Total Paid (XLM)': 'totalPaidXLM',
            'Most Recent Payment Date': 'mostRecentPaymentDate',
            'Award Type': 'awardType',
            'Category (from Project)': 'category'
        }
    
    def create_backup(self, file_path: str) -> str:
        """Create a backup of the original file."""
        backup_path = file_path + '.backup'
        shutil.copy2(file_path, backup_path)
        self.backups_created.append(backup_path)
        return backup_path
    
    def clean_value(self, value: str) -> Optional[str]:
        """Clean and normalize field values."""
        if not value or value.strip() == '' or value.strip().lower() in ['n/a', 'na', 'null', 'none', 'unknown']:
            return None
        return value.strip()
    
    def parse_boolean(self, value: str) -> Optional[bool]:
        """Parse boolean values from CSV."""
        if not value:
            return None
        value = value.strip().lower()
        if value in ['yes', 'true', '1', 'y']:
            return True
        elif value in ['no', 'false', '0', 'n']:
            return False
        return None
    
    def parse_percentage(self, value: str) -> Optional[float]:
        """Parse percentage values."""
        if not value:
            return None
        try:
            # Remove % sign if present
            value = value.replace('%', '').strip()
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def parse_amount(self, value: str) -> Optional[float]:
        """Parse monetary amounts."""
        if not value:
            return None
        try:
            # Remove commas and currency symbols
            value = re.sub(r'[,$]', '', str(value)).strip()
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def normalize_date(self, date_str: str) -> Optional[str]:
        """Normalize date to ISO8601 format."""
        if not date_str:
            return None
        
        try:
            # Try different date formats
            for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%m/%d/%y']:
                try:
                    date_obj = datetime.strptime(date_str.strip(), fmt)
                    return date_obj.strftime('%Y-%m-%d') + 'T00:00:00Z'
                except ValueError:
                    continue
            return None
        except Exception:
            return None
    
    def load_raw_data(self, round_number: int) -> List[Dict]:
        """Load raw CSV data for a specific round."""
        csv_files = [
            f"SCF #{round_number}.csv",
            f"SCF #{round_number} .csv"  # Handle space variation
        ]
        
        for csv_file in csv_files:
            csv_path = os.path.join(self.raw_data_dir, csv_file)
            if os.path.exists(csv_path):
                try:
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        return list(reader)
                except Exception as e:
                    print(f"❌ Error reading {csv_file}: {e}")
        
        return []
    
    def enhance_application(self, app: Dict, raw_data: Dict) -> Dict:
        """Enhance application with additional DAOIP-5 fields."""
        enhanced_app = app.copy()
        
        # Core DAOIP-5 fields
        if 'title' not in enhanced_app and self.clean_value(raw_data.get('Submission Title')):
            enhanced_app['title'] = self.clean_value(raw_data['Submission Title'])
        
        if 'description' not in enhanced_app and self.clean_value(raw_data.get('One-Sentence-Description')):
            enhanced_app['description'] = self.clean_value(raw_data['One-Sentence-Description'])
        
        # Enhanced funding information
        total_paid_usd = self.parse_amount(raw_data.get('Total Paid (USD)'))
        if total_paid_usd:
            enhanced_app['fundsPaid'] = [
                {
                    "amount": total_paid_usd,
                    "denomination": "USD"
                }
            ]
        
        total_paid_xlm = self.parse_amount(raw_data.get('Total Paid (XLM)'))
        if total_paid_xlm:
            if 'fundsPaid' not in enhanced_app:
                enhanced_app['fundsPaid'] = []
            enhanced_app['fundsPaid'].append({
                "amount": total_paid_xlm,
                "denomination": "XLM"
            })
        
        # Status and progress
        status = self.clean_value(raw_data.get('Status'))
        if status:
            enhanced_app['status'] = status
        
        completion_percent = self.parse_percentage(raw_data.get('Tranche Completion %'))
        if completion_percent is not None:
            enhanced_app['completionPercentage'] = completion_percent
        
        # Payment tracking
        recent_payment_date = self.normalize_date(raw_data.get('Most Recent Payment Date'))
        if recent_payment_date:
            enhanced_app['mostRecentPaymentDate'] = recent_payment_date
        
        latest_tranche = self.clean_value(raw_data.get('Latest Tranche (from Payments)'))
        if latest_tranche:
            enhanced_app['latestTranche'] = latest_tranche
        
        # Award type and category
        award_type = self.clean_value(raw_data.get('Award Type'))
        if award_type:
            enhanced_app['awardType'] = award_type
        
        category = self.clean_value(raw_data.get('Category (from Project)'))
        if category:
            enhanced_app['category'] = category
        
        # DAOIP-5 Extension fields
        extensions = {}
        
        # Technical details
        if self.clean_value(raw_data.get('Technical Architecture')):
            extensions['technicalArchitecture'] = self.clean_value(raw_data['Technical Architecture'])
        
        if self.clean_value(raw_data.get('Products & Services')):
            extensions['productsAndServices'] = self.clean_value(raw_data['Products & Services'])
        
        uses_soroban = self.parse_boolean(raw_data.get('Use Soroban?'))
        if uses_soroban is not None:
            extensions['usesSoroban'] = uses_soroban
        
        # Success metrics
        if self.clean_value(raw_data.get('Success Criteria')):
            extensions['successCriteria'] = self.clean_value(raw_data['Success Criteria'])
        
        if self.clean_value(raw_data.get('Traction Evidence')):
            extensions['tractionEvidence'] = self.clean_value(raw_data['Traction Evidence'])
        
        # Business information
        if self.clean_value(raw_data.get('Go-To-Market Plan')):
            extensions['goToMarketPlan'] = self.clean_value(raw_data['Go-To-Market Plan'])
        
        # Project deliverables
        deliverables = {}
        if self.clean_value(raw_data.get('Tranche 1 - Deliverables')):
            deliverables['tranche1'] = self.clean_value(raw_data['Tranche 1 - Deliverables'])
        if self.clean_value(raw_data.get('Tranche 2 - Testnet')):
            deliverables['tranche2'] = self.clean_value(raw_data['Tranche 2 - Testnet'])
        if self.clean_value(raw_data.get('Tranche 3 - Mainnet')):
            deliverables['tranche3'] = self.clean_value(raw_data['Tranche 3 - Mainnet'])
        
        if deliverables:
            extensions['deliverables'] = deliverables
        
        # Team information
        if self.clean_value(raw_data.get('Team Members')):
            extensions['teamMembers'] = self.clean_value(raw_data['Team Members'])
        
        # Additional URLs
        urls = {}
        if self.clean_value(raw_data.get('Website')):
            urls['website'] = self.clean_value(raw_data['Website'])
        if self.clean_value(raw_data.get('Code')):
            urls['codeRepository'] = self.clean_value(raw_data['Code'])
        if self.clean_value(raw_data.get('Video')):
            urls['videoURL'] = self.clean_value(raw_data['Video'])
        if self.clean_value(raw_data.get('Pitch Deck (from Project)')):
            urls['pitchDeck'] = self.clean_value(raw_data['Pitch Deck (from Project)'])
        
        if urls:
            extensions['urls'] = urls
        
        # Social media
        social = {}
        if self.clean_value(raw_data.get('LinkedIn (from Project)')):
            social['linkedIn'] = self.clean_value(raw_data['LinkedIn (from Project)'])
        if self.clean_value(raw_data.get('X (from Project)')):
            social['twitter'] = self.clean_value(raw_data['X (from Project)'])
        if self.clean_value(raw_data.get('Discord (from Project)')):
            social['discord'] = self.clean_value(raw_data['Discord (from Project)'])
        
        if social:
            extensions['socialMedia'] = social
        
        # Add extensions if any exist
        if extensions:
            enhanced_app['extensions'] = extensions
        
        return enhanced_app
    
    def find_matching_application(self, applications: List[Dict], project_name: str, submission_title: str) -> Optional[int]:
        """Find matching application by project name or title."""
        for i, app in enumerate(applications):
            # Try exact project name match first
            if app.get('projectName', '').lower() == project_name.lower():
                return i
            
            # Try partial matching
            if project_name.lower() in app.get('projectName', '').lower():
                return i
            
            # Try title matching if available
            if submission_title and app.get('title', '').lower() == submission_title.lower():
                return i
        
        return None
    
    def enhance_round_file(self, round_number: int) -> bool:
        """Enhance a specific round file with raw data."""
        json_file = f"scf-{round_number}_applications_uri.json"
        json_path = os.path.join(self.json_data_dir, json_file)
        
        if not os.path.exists(json_path):
            print(f"⚠️  JSON file not found: {json_file}")
            return False
        
        # Load raw data
        raw_data = self.load_raw_data(round_number)
        if not raw_data:
            print(f"⚠️  No raw data found for round {round_number}")
            return False
        
        # Create backup
        backup_path = self.create_backup(json_path)
        print(f"📁 Created backup: {os.path.basename(backup_path)}")
        
        # Load existing JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        enhanced_count = 0
        
        # Enhance applications
        for pool in json_data.get('grantPools', []):
            for app in pool.get('applications', []):
                project_name = app.get('projectName', '')
                
                # Find matching raw data
                matching_raw = None
                for raw_row in raw_data:
                    raw_project = raw_row.get('Project', '').strip()
                    raw_title = raw_row.get('Submission Title', '').strip()
                    
                    if (raw_project.lower() == project_name.lower() or 
                        project_name.lower() in raw_project.lower() or
                        raw_project.lower() in project_name.lower()):
                        matching_raw = raw_row
                        break
                
                if matching_raw:
                    original_app = json.dumps(app, sort_keys=True)
                    enhanced_app = self.enhance_application(app, matching_raw)
                    new_app = json.dumps(enhanced_app, sort_keys=True)
                    
                    if original_app != new_app:
                        app.update(enhanced_app)
                        enhanced_count += 1
        
        # Save enhanced file
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        if enhanced_count > 0:
            print(f"✅ Enhanced {json_file}: {enhanced_count} applications updated")
            self.enhanced_files.append(json_file)
            return True
        else:
            print(f"ℹ️  No enhancements needed for {json_file}")
            return False
    
    def enhance_all_rounds(self) -> None:
        """Enhance all round files."""
        print(f"🚀 Starting Stellar DAOIP-5 data enhancement")
        print(f"   Raw data directory: {self.raw_data_dir}")
        print(f"   JSON data directory: {self.json_data_dir}")
        
        # Find all available rounds
        available_rounds = []
        for filename in os.listdir(self.raw_data_dir):
            if filename.startswith('SCF #') and filename.endswith('.csv'):
                round_match = re.search(r'SCF #(\d+)', filename)
                if round_match:
                    available_rounds.append(int(round_match.group(1)))
        
        available_rounds.sort()
        print(f"   Found raw data for rounds: {available_rounds}")
        
        # Process each round
        for round_num in available_rounds:
            self.enhance_round_file(round_num)
        
        # Summary
        print(f"\n📊 Enhancement Summary:")
        print(f"   Files enhanced: {len(self.enhanced_files)}")
        print(f"   Backups created: {len(self.backups_created)}")
        
        if self.enhanced_files:
            print(f"   Enhanced files: {', '.join(self.enhanced_files)}")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    raw_data_dir = os.path.join(script_dir, '..', 'raw', 'stellar')
    json_data_dir = os.path.join(script_dir, '..', 'json', 'stellar')
    
    # Verify directories exist
    if not os.path.exists(raw_data_dir):
        print(f"❌ Error: Raw data directory not found: {raw_data_dir}")
        sys.exit(1)
    
    if not os.path.exists(json_data_dir):
        print(f"❌ Error: JSON data directory not found: {json_data_dir}")
        sys.exit(1)
    
    enhancer = StellarDataEnhancer(raw_data_dir, json_data_dir)
    enhancer.enhance_all_rounds()


if __name__ == "__main__":
    main()
