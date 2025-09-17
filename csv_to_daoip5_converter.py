#!/usr/bin/env python3
"""
Convert SCF CSV data to DAOIP-5 JSON format
"""

import pandas as pd
import json
import re
from datetime import datetime

def clean_project_name_for_id(name):
    """Convert project name to slug format for ID"""
    if pd.isna(name) or name == '':
        return 'unknown-project'
    
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', str(name))
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug.lower()
    
    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    
    return slug if slug else 'unknown-project'

def parse_urls_from_text(text):
    """Extract URLs from text content"""
    if pd.isna(text):
        return {}
    
    urls = {}
    url_patterns = {
        'website': r'Website:\s*(https?://[^\s\n]+)',
        'codeRepository': r'(?:Code|Repository|GitHub):\s*(https?://[^\s\n]+)',
        'videoURL': r'Video:\s*(https?://[^\s\n]+)'
    }
    
    text_str = str(text)
    for key, pattern in url_patterns.items():
        match = re.search(pattern, text_str, re.IGNORECASE)
        if match:
            urls[key] = match.group(1)
    
    return urls

def parse_social_media_from_text(text):
    """Extract social media URLs from text"""
    if pd.isna(text):
        return {}
    
    social = {}
    social_patterns = {
        'linkedIn': r'LinkedIn:\s*(https?://[^\s\n]+)',
        'twitter': r'(?:Twitter|X):\s*(https?://[^\s\n]+)', 
        'discord': r'Discord:\s*(https?://[^\s\n]+)'
    }
    
    text_str = str(text)
    for key, pattern in social_patterns.items():
        match = re.search(pattern, text_str, re.IGNORECASE)
        if match:
            social[key] = match.group(1)
    
    return social

def convert_csv_to_daoip5(csv_file, round_number):
    """Convert CSV file to DAOIP-5 JSON format"""
    
    print(f"Converting SCF #{round_number} to DAOIP-5 format...")
    
    # Read CSV
    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} projects from {csv_file}")
    
    # Create DAOIP-5 structure
    daoip5_data = {
        "@context": "http://www.daostar.org/schemas",
        "name": "Stellar",
        "type": "Foundation",
        "grantPools": [
            {
                "type": "GrantPool",
                "name": f"scf_{round_number}",
                "applications": []
            }
        ]
    }
    
    applications = []
    
    for idx, row in df.iterrows():
        # Clean and prepare data
        project_name = str(row.get('Submission / Project', '')).strip()
        if project_name == 'nan' or project_name == '':
            project_name = f"Project-{idx+1}"
        
        project_id_slug = clean_project_name_for_id(project_name)
        
        # Parse funding amount
        total_awarded = row.get('Total Awarded (USD)', '0')
        if pd.isna(total_awarded):
            total_awarded = 0
        else:
            # Clean currency formatting
            total_awarded = str(total_awarded).replace('$', '').replace(',', '')
            try:
                total_awarded = float(total_awarded)
            except:
                total_awarded = 0
        
        # Parse total paid
        total_paid = row.get('Total Paid (USD)', '0')
        if pd.isna(total_paid):
            total_paid = 0
        else:
            total_paid = str(total_paid).replace('$', '').replace(',', '')
            try:
                total_paid = float(total_paid)
            except:
                total_paid = 0
        
        # Parse XLM amount
        total_paid_xlm = row.get('Total Paid (XLM)', '0')
        if pd.isna(total_paid_xlm):
            total_paid_xlm = 0
        else:
            try:
                total_paid_xlm = float(total_paid_xlm)
            except:
                total_paid_xlm = 0
        
        # Build extensions object
        extensions = {}
        
        # Add stellar-specific fields
        stellar_fields = {
            'stellar.productsAndServices': 'Products & Services',
            'stellar.technicalArchitecture': 'Technical Architecture', 
            'stellar.successCriteria': 'Success Criteria',
            'stellar.goToMarketPlan': 'Go-To-Market Plan',
            'stellar.tractionEvidence': 'Traction Evidence',
            'stellar.tranche1Deliverables': 'Tranche 1 - Deliverables',
            'stellar.tranche2Testnet': 'Tranche 2 - Testnet',
            'stellar.tranche3Mainnet': 'Tranche 3 - Mainnet',
            'stellar.teamMembers': 'Team Members'
        }
        
        for ext_key, csv_key in stellar_fields.items():
            value = row.get(csv_key, '')
            if pd.notna(value) and str(value).strip() != '' and str(value).strip() != 'nan':
                extensions[ext_key] = str(value).strip()
        
        # Add URLs
        urls = {}
        if pd.notna(row.get('Website')):
            urls['website'] = str(row.get('Website')).strip()
        if pd.notna(row.get('Code')):
            urls['codeRepository'] = str(row.get('Code')).strip()
        if pd.notna(row.get('Video')):
            urls['videoURL'] = str(row.get('Video')).strip()
        
        if urls:
            extensions['stellar.urls'] = urls
        
        # Add social media
        social_media = {}
        linkedin_col = next((col for col in df.columns if 'LinkedIn' in col), None)
        twitter_col = next((col for col in df.columns if 'X (' in col), None) 
        discord_col = next((col for col in df.columns if 'Discord' in col), None)
        
        if linkedin_col and pd.notna(row.get(linkedin_col)):
            social_media['linkedIn'] = str(row.get(linkedin_col)).strip()
        if twitter_col and pd.notna(row.get(twitter_col)):
            social_media['twitter'] = str(row.get(twitter_col)).strip()  
        if discord_col and pd.notna(row.get(discord_col)):
            social_media['discord'] = str(row.get(discord_col)).strip()
        
        if social_media:
            extensions['stellar.socialMedia'] = social_media
        
        # Add award type
        award_type = row.get('Award Type', 'Build')
        if pd.notna(award_type):
            extensions['org.stellar.communityfund.awardType'] = str(award_type).strip()
        
        # Add funds paid information
        funds_paid = []
        if total_paid > 0:
            funds_paid.append({
                "amount": total_paid,
                "denomination": "USD"
            })
        if total_paid_xlm > 0:
            funds_paid.append({
                "amount": total_paid_xlm, 
                "denomination": "XLM"
            })
        
        if funds_paid:
            extensions['org.stellar.communityfund.fundsPaid'] = funds_paid
        
        # Create application object
        application = {
            "type": "GrantApplication",
            "id": f"daoip-5:stellar:grantPool:scf_{round_number}:grantApplication:{idx+1}",
            "grantPoolId": f"daoip-5:stellar:grantPool:scf_{round_number}",
            "grantPoolName": f"scf_{round_number}",
            "projectsURI": "",
            "projectId": f"daoip-5:stellar:project:{project_id_slug}",
            "projectName": project_name,
            "createdAt": "2024-12-01T00:00:00Z",  # Default timestamp
            "contentURI": "",
            "status": str(row.get('Status', 'Unknown')).strip(),
            "description": str(row.get('One-Sentence-Description', '')).strip()[:500] + ("..." if len(str(row.get('One-Sentence-Description', ''))) > 500 else ""),
            "fundsApprovedInUSD": total_awarded
        }
        
        if extensions:
            application["extensions"] = extensions
        
        applications.append(application)
    
    daoip5_data["grantPools"][0]["applications"] = applications
    
    return daoip5_data

def main():
    """Convert all SCF rounds to DAOIP-5 format"""
    
    rounds = [
        (36, 'SCF_36_Projects.csv'),
        (37, 'SCF_37_Projects.csv'), 
        (38, 'SCF_38_Projects.csv')
    ]
    
    for round_num, csv_file in rounds:
        try:
            # Convert to DAOIP-5
            daoip5_data = convert_csv_to_daoip5(csv_file, round_num)
            
            # Save to JSON file
            output_file = f'daoip-5/json/stellar/scf_{round_num}_applications_uri.json'
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(daoip5_data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Created {output_file} with {len(daoip5_data['grantPools'][0]['applications'])} applications")
            
        except Exception as e:
            print(f"❌ Error processing SCF #{round_num}: {e}")

if __name__ == "__main__":
    main()