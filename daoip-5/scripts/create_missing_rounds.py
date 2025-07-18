#!/usr/bin/env python3
"""
Create missing round files for SCF rounds 30-36
"""

import csv
import json
import os
from datetime import datetime

def create_round_file(round_number, csv_file_path, output_dir):
    """Create a DAOIP-5 compliant JSON file for a specific round."""
    
    applications = []
    
    # Read CSV data
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            app_id = 1
            
            for row in reader:
                # Parse basic information
                project_name = row.get('Project', '').strip()
                submission_title = row.get('Submission Title', '').strip()
                
                if not project_name:
                    continue
                
                # Create application entry
                application = {
                    "type": "GrantApplication",
                    "id": f"daoip5:stellar:grantApplication:{app_id}",
                    "grantPoolId": f"daoip5:stellar:grantPool:scf-{round_number}",
                    "grantPoolName": f"scf-{round_number}",
                    "projectsURI": row.get('Submission URL', ''),
                    "projectId": f"daoip5:stellar:project:{project_name.lower().replace(' ', '-').replace('&', 'and').replace(',', '').replace('(', '').replace(')', '').replace(':', '')}",
                    "projectName": project_name,
                    "createdAt": "2024-12-01T00:00:00Z",  # Default date for newer rounds
                    "contentURI": row.get('Submission URL', ''),
                    "title": submission_title or project_name,
                    "status": row.get('Status', 'Unknown'),
                    "category": row.get('Category (from Project)', 'Applications')
                }
                
                # Add description if available
                description = row.get('One-Sentence-Description', '').strip()
                if description:
                    application["description"] = description
                
                # Parse funding information
                total_awarded = row.get('Total Awarded (USD)', '').replace('$', '').replace(',', '').strip()
                total_paid_usd = row.get('Total Paid (USD)', '').replace('$', '').replace(',', '').strip()
                total_paid_xlm = row.get('Total Paid (XLM)', '').replace(',', '').strip()
                
                if total_awarded:
                    try:
                        application["fundsApprovedInUSD"] = float(total_awarded)
                    except ValueError:
                        pass
                
                # Add funding arrays
                funds_paid = []
                if total_paid_usd:
                    try:
                        funds_paid.append({
                            "amount": float(total_paid_usd),
                            "denomination": "USD"
                        })
                    except ValueError:
                        pass
                
                if total_paid_xlm:
                    try:
                        funds_paid.append({
                            "amount": float(total_paid_xlm),
                            "denomination": "XLM"
                        })
                    except ValueError:
                        pass
                
                if funds_paid:
                    application["fundsPaid"] = funds_paid
                
                # Add award type and payment info
                award_type = row.get('Award Type', '').strip()
                if award_type:
                    application["awardType"] = award_type
                
                latest_tranche = row.get('Latest Tranche (from Payments)', '').strip()
                if latest_tranche:
                    application["latestTranche"] = latest_tranche
                
                payment_date = row.get('Most Recent Payment Date', '').strip()
                if payment_date:
                    application["mostRecentPaymentDate"] = payment_date
                
                # DAOIP-5 Extensions for Stellar-specific data
                extensions = {}
                
                # Technical information
                if row.get('Technical Architecture'):
                    extensions['stellar.technicalArchitecture'] = row['Technical Architecture'].strip()
                
                if row.get('Products & Services'):
                    extensions['stellar.productsAndServices'] = row['Products & Services'].strip()
                
                uses_soroban = row.get('Use Soroban?', '').strip().lower()
                if uses_soroban in ['yes', 'true', '1']:
                    extensions['stellar.usesSoroban'] = True
                elif uses_soroban in ['no', 'false', '0']:
                    extensions['stellar.usesSoroban'] = False
                
                # Success criteria and business info
                if row.get('Success Criteria'):
                    extensions['stellar.successCriteria'] = row['Success Criteria'].strip()
                
                if row.get('Go-To-Market Plan'):
                    extensions['stellar.goToMarketPlan'] = row['Go-To-Market Plan'].strip()
                
                if row.get('Traction Evidence'):
                    extensions['stellar.tractionEvidence'] = row['Traction Evidence'].strip()
                
                # Deliverables
                if row.get('Tranche 1 - Deliverables'):
                    extensions['stellar.tranche1Deliverables'] = row['Tranche 1 - Deliverables'].strip()
                
                if row.get('Tranche 2 - Testnet'):
                    extensions['stellar.tranche2Testnet'] = row['Tranche 2 - Testnet'].strip()
                
                if row.get('Tranche 3 - Mainnet'):
                    extensions['stellar.tranche3Mainnet'] = row['Tranche 3 - Mainnet'].strip()
                
                # Team information
                if row.get('Team Members'):
                    extensions['stellar.teamMembers'] = row['Team Members'].strip()
                
                # URLs
                stellar_urls = {}
                if row.get('Website'):
                    stellar_urls['website'] = row['Website'].strip()
                if row.get('Code'):
                    stellar_urls['codeRepository'] = row['Code'].strip()
                if row.get('Video'):
                    stellar_urls['videoURL'] = row['Video'].strip()
                if row.get('Pitch Deck (from Project)'):
                    stellar_urls['pitchDeck'] = row['Pitch Deck (from Project)'].strip()
                
                if stellar_urls:
                    extensions['stellar.urls'] = stellar_urls
                
                # Social media
                stellar_social = {}
                if row.get('LinkedIn (from Project)'):
                    stellar_social['linkedIn'] = row['LinkedIn (from Project)'].strip()
                if row.get('X (from Project)'):
                    stellar_social['twitter'] = row['X (from Project)'].strip()
                if row.get('Discord (from Project)'):
                    stellar_social['discord'] = row['Discord (from Project)'].strip()
                
                if stellar_social:
                    extensions['stellar.socialMedia'] = stellar_social
                
                # Add extensions if any exist
                if extensions:
                    application["extensions"] = extensions
                
                applications.append(application)
                app_id += 1
    
    except FileNotFoundError:
        print(f"❌ CSV file not found: {csv_file_path}")
        return False
    except Exception as e:
        print(f"❌ Error processing {csv_file_path}: {e}")
        return False
    
    # Create JSON structure
    json_data = {
        "@context": "http://www.daostar.org/schemas",
        "name": "Stellar",
        "type": "Foundation",
        "grantPools": [
            {
                "type": "GrantPool",
                "name": f"scf-{round_number}",
                "applications": applications
            }
        ]
    }
    
    # Write JSON file
    output_file = os.path.join(output_dir, f"scf-{round_number}_applications_uri.json")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Created {output_file}: {len(applications)} applications")
        return True
    
    except Exception as e:
        print(f"❌ Error writing {output_file}: {e}")
        return False

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    raw_data_dir = os.path.join(script_dir, '..', 'raw', 'stellar')
    json_data_dir = os.path.join(script_dir, '..', 'json', 'stellar')
    
    print("🚀 Creating missing round files for SCF 30-36")
    
    rounds_to_create = [30, 31, 32, 33, 34, 35, 36]
    created_count = 0
    
    for round_num in rounds_to_create:
        csv_file = os.path.join(raw_data_dir, f"SCF #{round_num}.csv")
        if round_num == 34:
            csv_file = os.path.join(raw_data_dir, f"SCF #{round_num} .csv")  # Handle space in filename
        
        if os.path.exists(csv_file):
            if create_round_file(round_num, csv_file, json_data_dir):
                created_count += 1
        else:
            print(f"⚠️  CSV file not found for round {round_num}: {csv_file}")
    
    print(f"\n📊 Summary:")
    print(f"   Files created: {created_count}/{len(rounds_to_create)}")

if __name__ == "__main__":
    main()
