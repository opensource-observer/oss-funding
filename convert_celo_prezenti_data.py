#!/usr/bin/env python3
"""
Convert Celo Prezenti Q4 2024 grant data to DAOIP-5 format
Process Growth, Pilot, and Micro grant pools with proper descriptions
"""

import csv
import json
import re
from datetime import datetime

def clean_project_id(project_name):
    """Convert project name to a clean project ID"""
    if not project_name:
        return "unknown-project"
    
    clean_id = re.sub(r'[^a-zA-Z0-9\s&-]', '', str(project_name))
    clean_id = re.sub(r'[\s&]+', '-', clean_id)
    clean_id = clean_id.lower().strip('-')
    clean_id = re.sub(r'-+', '-', clean_id)
    
    return clean_id if clean_id else "unknown-project"

def parse_date(date_str):
    """Parse date string to ISO format"""
    if not date_str or str(date_str).strip() == '':
        return "2024-10-01T00:00:00Z"  # Default to Q4 2024 start
    
    try:
        # Handle format like "10/10/24, 1:18 PM"
        date_part = str(date_str).split(',')[0].strip()
        date_obj = datetime.strptime(date_part, '%m/%d/%y')
        return date_obj.strftime('%Y-%m-%dT00:00:00Z')
    except:
        return "2024-10-01T00:00:00Z"

def process_celo_csv(csv_file, pool_type):
    """Process a Celo Prezenti CSV file"""
    
    applications = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8-sig', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for idx, row in enumerate(reader, start=1):
                # Extract key fields
                title = str(row.get('Title', '')).strip()
                project_name = str(row.get('Project Name', title)).strip()
                
                if not project_name:
                    continue
                
                project_id = clean_project_id(project_name)
                
                # Parse other fields
                status = str(row.get('Proposal Status', '')).strip()
                publish_date = parse_date(row.get('Publish Date', ''))
                contact_email = str(row.get('Contact Email', '')).strip()
                payee_address = str(row.get('ERC-20 Payee Address', '')).strip()
                category = str(row.get('Category', '')).strip()
                proposal_url = str(row.get('Proposal Url', '')).strip()
                team_overview = str(row.get('Team Overview:', '')).strip()
                region = str(row.get('Region', '')).strip()
                team_location = str(row.get('Team Location(s):', '')).strip()
                logo = str(row.get('Logo', '')).strip()
                
                # Determine funding status - Failed means rejected, Passed means awarded
                is_awarded = status.lower() == 'passed'
                
                # Build the application object
                application = {
                    "type": "GrantApplication",
                    "id": f"daoip-5:celo:grantPool:mint_{pool_type.lower()}:grantApplication:{idx}",
                    "grantPoolId": f"daoip-5:celo:grantPool:mint_{pool_type.lower()}",
                    "grantPoolName": f"mint_{pool_type.lower()}",
                    "projectsURI": proposal_url,
                    "projectId": f"daoip-5:celo:project:{project_id}",
                    "projectName": project_name,
                    "createdAt": publish_date,
                    "contentURI": proposal_url,
                    "description": title,
                    "status": "Awarded" if is_awarded else "Rejected",
                    "extensions": {
                        "celo.category": category,
                        "celo.poolType": pool_type,
                        "celo.round": "Mint",
                        "celo.quarter": "Q4 2024",
                        "celo.grantManagementTool": "Prezenti",
                        "celo.contactEmail": contact_email,
                        "celo.payeeAddress": payee_address,
                        "celo.teamOverview": team_overview,
                        "celo.region": region,
                        "celo.teamLocation": team_location,
                        "celo.proposalStep": str(row.get('Proposal Step', '')).strip(),
                        "celo.originalStatus": status
                    }
                }
                
                # Add logo if available
                if logo and logo.startswith('http'):
                    application["extensions"]["celo.logoURL"] = logo
                
                # Add reviewer notes if available
                reviewer_notes = str(row.get('Reviewer Notes', '')).strip()
                if reviewer_notes:
                    application["extensions"]["celo.reviewerNotes"] = reviewer_notes
                
                # Add additional fields based on pool type
                if pool_type == "Growth":
                    prior_work = str(row.get('Prior Work Examples:', '')).strip()
                    if prior_work:
                        application["extensions"]["celo.priorWorkExamples"] = prior_work
                
                # Clean up empty extension values
                application["extensions"] = {k: v for k, v in application["extensions"].items() 
                                          if v not in [None, '', 'N/A', 'n/a']}
                
                applications.append(application)
                print(f"  ✅ {pool_type}: {project_name} ({status})")
        
        return applications
        
    except Exception as e:
        print(f"❌ Error processing {csv_file}: {e}")
        return []

def create_celo_daoip5_files():
    """Create DAOIP-5 JSON files for all Celo grant pools"""
    
    # Define grant pool descriptions
    pool_descriptions = {
        "Growth": "The Growth pool supports established projects with proven traction looking to scale and expand their impact within the Celo ecosystem. These grants focus on projects that can demonstrate significant user adoption, revenue generation, or ecosystem growth potential.",
        "Pilot": "The Pilot pool funds experimental projects and early-stage initiatives that show promise for innovation within the Celo ecosystem. These grants support teams testing new concepts, building prototypes, or exploring novel use cases for blockchain technology.",
        "Micro": "The Micro pool provides smaller grants for grassroots projects, community initiatives, and individual contributors. These grants are designed to lower barriers to entry and support diverse voices within the Celo ecosystem."
    }
    
    # Process each CSV file
    csv_files = [
        ('attached_assets/Prezenti - Mint round data pull (Q4 2024) for Celo PG - Mint - growth_1758510925312.csv', 'Growth'),
        ('attached_assets/Prezenti - Mint round data pull (Q4 2024) for Celo PG - Mint - pilot_1758510928116.csv', 'Pilot'),
        ('attached_assets/Prezenti - Mint round data pull (Q4 2024) for Celo PG - Mint - micro_1758510930609.csv', 'Micro')
    ]
    
    all_pools = []
    
    for csv_file, pool_type in csv_files:
        print(f"\n=== Processing Celo {pool_type} Pool ===")
        applications = process_celo_csv(csv_file, pool_type)
        
        if applications:
            # Count awarded vs total
            awarded_count = len([app for app in applications if app["status"] == "Awarded"])
            total_count = len(applications)
            
            # Create grant pool data
            grant_pool = {
                "type": "GrantPool",
                "id": f"daoip-5:celo:grantPool:mint_{pool_type.lower()}",
                "name": f"mint_{pool_type.lower()}",
                "description": pool_descriptions[pool_type],
                "isOpen": False,  # Q4 2024 round is closed
                "applicationsURI": f"https://raw.githubusercontent.com/opensource-observer/oss-funding/refs/heads/main/daoip-5/json/celo/mint_{pool_type.lower()}_applications_uri.json",
                "requiredCredentials": [
                    "KYC",
                    "Project Verification"
                ],
                "extensions": {
                    "celo.round": "Mint",
                    "celo.quarter": "Q4 2024",
                    "celo.poolType": pool_type,
                    "celo.grantManagementTool": "Prezenti",
                    "celo.forumURL": "https://forum.celo.org/t/prezenti-opens-mint-round-for-applications/9139",
                    "celo.totalApplications": total_count,
                    "celo.awardedApplications": awarded_count,
                    "celo.successRate": round((awarded_count / total_count) * 100, 1) if total_count > 0 else 0.0
                }
            }
            
            all_pools.append(grant_pool)
            
            # Create applications URI file
            applications_data = {
                "@context": "http://www.daostar.org/schemas",
                "name": "Celo Public Goods",
                "type": "Entity",
                "grantPools": [
                    {
                        "type": "GrantPool",
                        "name": f"mint_{pool_type.lower()}",
                        "applications": applications
                    }
                ]
            }
            
            # Save applications JSON
            output_file = f'daoip-5/json/celo/mint_{pool_type.lower()}_applications_uri.json'
            with open(output_file, 'w') as f:
                json.dump(applications_data, f, indent=4)
            
            print(f"✅ Created {output_file}")
            print(f"   {total_count} applications, {awarded_count} awarded ({round((awarded_count / total_count) * 100, 1)}% success rate)")
    
    # Update the main Celo grants pool file
    if all_pools:
        grants_pool_data = {
            "@context": "http://www.daostar.org/schemas",
            "name": "Celo Public Goods",
            "type": "Entity",
            "grantPools": all_pools
        }
        
        # Save grants pool JSON
        output_file = 'daoip-5/json/celo/grants_pool.json'
        with open(output_file, 'w') as f:
            json.dump(grants_pool_data, f, indent=4)
        
        print(f"\n✅ Updated {output_file}")
        print(f"   Added {len(all_pools)} Celo grant pools")
        
        return True
    
    return False

if __name__ == "__main__":
    print("=== Converting Celo Prezenti Q4 2024 Data to DAOIP-5 ===")
    success = create_celo_daoip5_files()
    
    if success:
        print("✅ Celo Prezenti data conversion completed successfully!")
    else:
        print("❌ Celo Prezenti data conversion failed!")