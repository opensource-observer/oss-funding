#!/usr/bin/env python3
"""
Enhance grants_pool.json with additional SCF round data from CSV
Maps fields to DAOIP-5 standard where possible, adds rest to extensions
"""

import csv
import json
import re
from datetime import datetime

def parse_currency(amount_str):
    """Parse currency amount string to float"""
    if not amount_str or str(amount_str).strip() == '':
        return 0.0
    
    clean_amount = re.sub(r'[\$,]', '', str(amount_str))
    try:
        return float(clean_amount)
    except:
        return 0.0

def parse_percentage(pct_str):
    """Parse percentage string to float"""
    if not pct_str or str(pct_str).strip() == '':
        return 0.0
    
    clean_pct = re.sub(r'[%]', '', str(pct_str))
    try:
        return float(clean_pct)
    except:
        return 0.0

def parse_date(date_str):
    """Parse date string to ISO format"""
    if not date_str or str(date_str).strip() == '':
        return None
    
    try:
        for fmt in ['%B %d, %Y', '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
            try:
                date_obj = datetime.strptime(str(date_str).strip(), fmt)
                return date_obj.strftime('%Y-%m-%dT00:00:00Z')
            except:
                continue
    except:
        pass
    
    return None

def extract_round_number(name):
    """Extract round number from SCF name"""
    match = re.search(r'#(\d+)', name)
    return int(match.group(1)) if match else 0

def determine_status(phase):
    """Determine if grant pool is open based on phase"""
    if not phase:
        return False
    phase_lower = str(phase).lower()
    return phase_lower not in ['ended', 'completed', 'closed']

def read_scf_round_data(csv_file):
    """Read SCF round data from CSV file"""
    
    round_data = {}
    
    try:
        with open(csv_file, 'r', encoding='utf-8-sig', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                name = str(row.get('Name', '')).strip()
                if not name or not name.startswith('SCF #'):
                    continue
                
                round_number = extract_round_number(name)
                if round_number == 0:
                    continue
                
                # Map fields to DAOIP-5 structure with extensions
                round_info = {
                    # DAOIP-5 standard fields
                    'description': str(row.get('Description', '')).strip(),
                    'isOpen': determine_status(row.get('Phase', '')),
                    
                    # Extensions for SCF-specific data
                    'extensions': {
                        'stellar.quarter': str(row.get('Quarter, Year', '')).strip(),
                        'stellar.phase': str(row.get('Phase', '')).strip(),
                        'stellar.appliedProjectAbstracts': parse_currency(row.get('Applied Project Abstracts', 0)),
                        'stellar.appliedSubmissions': parse_currency(row.get('Applied Submissions', 0)),
                        'stellar.awardedSubmissions': parse_currency(row.get('Awarded Submissions', 0)),
                        'stellar.percentAwarded': parse_percentage(row.get('% Awarded', 0)),
                        'stellar.totalAwardedUSD': parse_currency(row.get('Total Awarded (USD)', 0)),
                        'stellar.totalPaidUSD': parse_currency(row.get('Total Paid (USD)', 0)),
                        'stellar.totalPaidXLM': parse_currency(row.get('Total Paid (XLM)', 0)),
                        'stellar.averageAwardedUSD': parse_currency(row.get('Average Awarded in USD', 0)),
                        'stellar.votersNumber': parse_currency(row.get('Voters Number', 0)),
                        'stellar.roundURL': str(row.get('Round URL', '')).strip(),
                        'stellar.type': str(row.get('Type', '')).strip(),
                        'stellar.scfVersion': str(row.get('SCF Version', '')).strip(),
                        'stellar.roundRecap': str(row.get('Round Recap', '')).strip(),
                        'stellar.year': str(row.get('Year', '')).strip(),
                    }
                }
                
                # Add date fields
                submission_open = parse_date(row.get('Submission Open Date', ''))
                submission_close = parse_date(row.get('Submission Close Date', ''))
                
                if submission_open:
                    round_info['extensions']['stellar.submissionOpenDate'] = submission_open
                if submission_close:
                    round_info['extensions']['stellar.submissionCloseDate'] = submission_close
                
                # Add additional date fields to extensions
                date_fields = [
                    'Initial Review Open Date', 'Initial Review Close Date',
                    'Award Submission Open Date', 'Award Submission Close Date',
                    'Panel Review Open Date', 'Panel Review Close Date',
                    'Community Vote Open Date', 'Community Vote Close Date',
                    'Notification and Award Distribution Open Date', 'Notification and Award Distribution Close Date',
                    'Cohort Open Date', 'Cohort Close Date'
                ]
                
                for field in date_fields:
                    date_value = parse_date(row.get(field, ''))
                    if date_value:
                        extension_key = f"stellar.{field.lower().replace(' ', '').replace('date', 'Date')}"
                        round_info['extensions'][extension_key] = date_value
                
                # Add list fields
                submissions = str(row.get('Submissions', '')).strip()
                if submissions:
                    round_info['extensions']['stellar.submissions'] = submissions
                
                projects = str(row.get('Project (from Submissions)', '')).strip()
                if projects:
                    round_info['extensions']['stellar.projectsFromSubmissions'] = projects
                
                # Add image if available
                image = str(row.get('Image', '')).strip()
                if image:
                    round_info['extensions']['stellar.imageURL'] = image
                
                round_data[round_number] = round_info
                print(f"✅ Processed SCF #{round_number}: {round_info['extensions']['stellar.quarter']}")
        
        print(f"\nSuccessfully processed {len(round_data)} SCF rounds")
        return round_data
        
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return {}

def enhance_grants_pool_json():
    """Enhance grants_pool.json with additional SCF round data"""
    
    csv_file = 'attached_assets/Build Award Rounds-Grid view_1758510369047.csv'
    grants_pool_file = 'daoip-5/json/stellar/grants_pool.json'
    
    # Read the CSV data
    round_data = read_scf_round_data(csv_file)
    
    if not round_data:
        print("❌ No round data found")
        return False
    
    # Read existing grants pool JSON
    try:
        with open(grants_pool_file, 'r') as f:
            grants_pool = json.load(f)
    except Exception as e:
        print(f"❌ Error reading grants pool JSON: {e}")
        return False
    
    # Update grant pools with additional data
    updated_count = 0
    
    for grant_pool in grants_pool.get('grantPools', []):
        pool_name = grant_pool.get('name', '')
        
        # Extract round number from pool name (e.g., "scf_35" -> 35)
        match = re.search(r'scf_(\d+)', pool_name)
        if not match:
            continue
        
        round_number = int(match.group(1))
        
        if round_number in round_data:
            round_info = round_data[round_number]
            
            # Update DAOIP-5 standard fields
            if round_info['description']:
                grant_pool['description'] = round_info['description']
            
            grant_pool['isOpen'] = round_info['isOpen']
            
            # Add extensions
            if 'extensions' not in grant_pool:
                grant_pool['extensions'] = {}
            
            grant_pool['extensions'].update(round_info['extensions'])
            
            # Clean up empty extension values
            grant_pool['extensions'] = {k: v for k, v in grant_pool['extensions'].items() 
                                     if v not in [None, '', 0, '0']}
            
            updated_count += 1
            print(f"✅ Enhanced SCF #{round_number}: {grant_pool['name']}")
    
    # Save the enhanced JSON
    try:
        with open(grants_pool_file, 'w') as f:
            json.dump(grants_pool, f, indent=4)
        
        print(f"\n✅ Successfully enhanced {updated_count} grant pools in {grants_pool_file}")
        
        # Validate JSON structure
        with open(grants_pool_file, 'r') as f:
            json.load(f)
        print("✅ JSON structure validation passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving enhanced JSON: {e}")
        return False

if __name__ == "__main__":
    print("=== Enhancing Grants Pool JSON with SCF Round Data ===")
    success = enhance_grants_pool_json()
    
    if success:
        print("✅ Grants pool enhancement completed successfully!")
    else:
        print("❌ Grants pool enhancement failed!")