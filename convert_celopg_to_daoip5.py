#!/usr/bin/env python3
import json
import os
import re
from datetime import datetime

def normalize_amount(amount_str):
    """Convert amount to float, handling various formats"""
    if not amount_str or amount_str == "" or amount_str is None:
        return 0.0
    if isinstance(amount_str, (int, float)):
        return float(amount_str)
    # Remove any currency symbols and convert
    clean_amount = re.sub(r'[^\d.-]', '', str(amount_str))
    try:
        return float(clean_amount) if clean_amount else 0.0
    except:
        return 0.0

def convert_timestamp(timestamp_str):
    """Convert timestamp to ISO format"""
    if not timestamp_str:
        return "2024-01-01T00:00:00Z"
    try:
        # Handle timezone format +00:00
        if '+' in timestamp_str:
            timestamp_str = timestamp_str.replace('+00:00', 'Z')
        elif timestamp_str.endswith('Z'):
            pass
        else:
            timestamp_str += 'Z'
        return timestamp_str
    except:
        return "2024-01-01T00:00:00Z"

def extract_round_id(filename):
    """Extract round ID from filename"""
    match = re.search(r'round_(\d+)', filename)
    return match.group(1) if match else "unknown"

def create_grants_pool():
    """Create grants_pool.json from roundsOnCelo.json"""
    print("Creating grants_pool.json...")
    
    with open('daoip-5/raw/CeloPG/roundsOnCelo.json', 'r') as f:
        rounds_data = json.load(f)
    
    grant_pools = []
    
    for round_info in rounds_data['data']['rounds']:
        round_id = str(round_info['id'])
        round_name = round_info['roundMetadata']['name']
        
        # Find corresponding application file
        app_files = [f for f in os.listdir('daoip-5/raw/CeloPG/') 
                    if f.startswith('round_') and f.endswith('.json')]
        
        # Match round ID in filename or use the round as fallback
        applications_uri = f"https://raw.githubusercontent.com/opensource-observer/oss-funding/refs/heads/main/daoip-5/json/CeloPG/round_{round_id}_applications_uri.json"
        
        pool_entry = {
            "type": "GrantPool",
            "id": f"daoip-5:celopg:grantPool:round_{round_id}",
            "name": f"round_{round_id}",
            "description": f"Grants pool for {round_name}.",
            "isOpen": False,
            "applicationsURI": applications_uri,
            "requiredCredentials": ["DAO Attestation", "KYC"],
            "extensions": {
                "celopg.roundName": round_name,
                "celopg.chainId": round_info.get('chainId', 42220),
                "celopg.fundedAmountInUsd": normalize_amount(round_info.get('fundedAmountInUsd', 0)),
                "celopg.totalAmountDonatedInUsd": normalize_amount(round_info.get('totalAmountDonatedInUsd', 0)),
                "celopg.matchAmountInUsd": normalize_amount(round_info.get('matchAmountInUsd', 0)),
                "celopg.timestamp": convert_timestamp(round_info.get('timestamp')),
                "celopg.applicationsStartTime": convert_timestamp(round_info.get('applicationsStartTime')),
                "celopg.applicationsEndTime": convert_timestamp(round_info.get('applicationsEndTime')),
                "celopg.donationsStartTime": convert_timestamp(round_info.get('donationsStartTime')),
                "celopg.donationsEndTime": convert_timestamp(round_info.get('donationsEndTime')),
                "celopg.strategyName": round_info.get('strategyName', ''),
                "celopg.totalDonationsCount": round_info.get('totalDonationsCount', 0),
                "celopg.uniqueDonorsCount": round_info.get('uniqueDonorsCount', 0),
                "celopg.roundType": round_info.get('roundMetadata', {}).get('roundType', ''),
                "celopg.strategyAddress": round_info.get('strategyAddress', ''),
                "celopg.strategyId": round_info.get('strategyId', '')
            }
        }
        
        # Add quadratic funding config if available
        qf_config = round_info.get('roundMetadata', {}).get('quadraticFundingConfig', {})
        if qf_config:
            pool_entry['extensions']['celopg.quadraticFunding'] = {
                "matchingCap": qf_config.get('matchingCap', False),
                "matchingCapAmount": qf_config.get('matchingCapAmount', 0),
                "matchingFundsAvailable": qf_config.get('matchingFundsAvailable', 0)
            }
        
        # Add eligibility info
        eligibility = round_info.get('roundMetadata', {}).get('eligibility', {})
        if eligibility:
            pool_entry['extensions']['celopg.eligibility'] = {
                "description": eligibility.get('description', ''),
                "requirements": [req.get('requirement', '') for req in eligibility.get('requirements', [])]
            }
        
        grant_pools.append(pool_entry)
    
    grants_pool_data = {
        "@context": "http://www.daostar.org/schemas",
        "name": "Celo Public Goods",
        "type": "Entity",
        "grantPools": grant_pools
    }
    
    with open('daoip-5/json/CeloPG/grants_pool.json', 'w') as f:
        json.dump(grants_pool_data, f, indent=4)
    
    print(f"Created grants_pool.json with {len(grant_pools)} grant pools")
    return len(grant_pools)

def convert_application_to_daoip5(app_data, round_id):
    """Convert a single application to DAOIP-5 format"""
    
    # Extract basic info
    app_id = app_data.get('id', 'unknown')
    anchor_address = app_data.get('anchorAddress', '')
    created_by = app_data.get('createdByAddress', '')
    
    # Parse application metadata
    metadata = app_data.get('metadata', {})
    application = metadata.get('application', {})
    answers = application.get('answers', [])
    
    # Build answers dictionary for easier access
    answers_dict = {}
    for answer in answers:
        question = answer.get('question', '')
        answer_text = answer.get('answer', '')
        answers_dict[question] = answer_text
    
    # Extract project name from answers or use fallback
    project_name = answers_dict.get('Project Name', 
                                   answers_dict.get('Organization Name', 
                                                   f"Application {app_id}"))
    
    # Create project ID from name
    project_id_name = re.sub(r'[^a-zA-Z0-9\s-]', '', project_name.lower())
    project_id_name = re.sub(r'\s+', '-', project_id_name.strip())
    if not project_id_name:
        project_id_name = f"application-{app_id}"
    
    # Get donation/funding info
    donations_agg = app_data.get('donationsAggregate', {}).get('aggregate', {})
    total_donations = donations_agg.get('sum', {}).get('amountInUsd', 0) or 0
    
    # Build the DAOIP-5 application entry
    daoip5_app = {
        "type": "GrantApplication",
        "id": f"daoip-5:celopg:grantPool:round_{round_id}:grantApplication:{app_id}",
        "grantPoolId": f"daoip-5:celopg:grantPool:round_{round_id}",
        "grantPoolName": f"round_{round_id}",
        "projectsURI": "",
        "projectId": f"daoip-5:celopg:project:{project_id_name}",
        "projectName": project_name,
        "createdAt": convert_timestamp(None),
        "contentURI": "",
        "status": "Submitted",
        "description": answers_dict.get('Project Description', 
                                       answers_dict.get('Please provide a brief description of your project', '')),
        "fundsApprovedInUSD": normalize_amount(total_donations)
    }
    
    # Build comprehensive extensions
    extensions = {
        "celopg.anchorAddress": anchor_address,
        "celopg.createdByAddress": created_by,
        "celopg.chainId": app_data.get('chainId', 42220),
        "celopg.createdAtBlock": app_data.get('createdAtBlock', 0),
        "celopg.donationsCount": donations_agg.get('count', 0),
        "celopg.signature": metadata.get('signature', ''),
        "celopg.answers": {},
        "celopg.urls": {},
        "celopg.socialMedia": {}
    }
    
    # Process all answers into extensions
    for answer in answers:
        question = answer.get('question', '')
        answer_text = answer.get('answer', '')
        question_id = answer.get('questionId', '')
        
        if question and answer_text:
            # Convert answer_text to string if it's a list or other type
            answer_str = str(answer_text) if not isinstance(answer_text, str) else answer_text
            
            # Clean question for use as key
            clean_question = re.sub(r'[^a-zA-Z0-9\s]', '', question)
            clean_question = re.sub(r'\s+', '_', clean_question.strip().lower())
            extensions['celopg.answers'][clean_question] = answer_str
            
            # Extract specific fields
            if 'email' in question.lower():
                extensions['celopg.emailAddress'] = answer_str
            elif 'funding' in question.lower() and 'source' in question.lower():
                extensions['celopg.fundingSources'] = answer_str
            elif 'team' in question.lower() and 'size' in question.lower():
                extensions['celopg.teamSize'] = normalize_amount(answer_str)
            elif 'website' in question.lower() or 'url' in question.lower():
                extensions['celopg.urls']['website'] = answer_str
            elif 'github' in question.lower() or 'repository' in question.lower():
                extensions['celopg.urls']['codeRepository'] = answer_str
            elif 'twitter' in question.lower() or ('x.com' in answer_str.lower()):
                extensions['celopg.socialMedia']['twitter'] = answer_str
            elif 'linkedin' in question.lower():
                extensions['celopg.socialMedia']['linkedIn'] = answer_str
            elif 'discord' in question.lower():
                extensions['celopg.socialMedia']['discord'] = answer_str
    
    # Add donation details if available
    donations = app_data.get('donations', [])
    if donations:
        extensions['celopg.donations'] = []
        for donation in donations[:10]:  # Limit to prevent too much data
            donation_info = {
                "donorAddress": donation.get('donorAddress', ''),
                "amount": normalize_amount(donation.get('amount', 0)),
                "amountInUsd": normalize_amount(donation.get('amountInUsd', 0)),
                "timestamp": convert_timestamp(donation.get('timestamp'))
            }
            extensions['celopg.donations'].append(donation_info)
    
    # Add payout information if available
    payouts = app_data.get('applicationsPayouts', [])
    if payouts:
        extensions['celopg.payouts'] = []
        for payout in payouts:
            payout_info = {
                "amount": normalize_amount(payout.get('amount', 0)),
                "amountInUsd": normalize_amount(payout.get('amountInUsd', 0)),
                "timestamp": convert_timestamp(payout.get('timestamp'))
            }
            extensions['celopg.payouts'].append(payout_info)
    
    daoip5_app['extensions'] = extensions
    
    return daoip5_app

def convert_round_applications(filename):
    """Convert a round applications file to DAOIP-5 format"""
    round_id = extract_round_id(filename)
    
    print(f"Converting {filename} (Round {round_id})...")
    
    with open(f'daoip-5/raw/CeloPG/{filename}', 'r') as f:
        round_data = json.load(f)
    
    applications = round_data.get('data', {}).get('applications', [])
    
    daoip5_applications = []
    for app in applications:
        daoip5_app = convert_application_to_daoip5(app, round_id)
        daoip5_applications.append(daoip5_app)
    
    # Create the DAOIP-5 structure
    daoip5_structure = {
        "@context": "http://www.daostar.org/schemas",
        "name": f"Celo Public Goods Round {round_id} Applications",
        "type": "Entity",
        "grantPools": [
            {
                "type": "GrantPool",
                "id": f"daoip-5:celopg:grantPool:round_{round_id}",
                "name": f"round_{round_id}",
                "applications": daoip5_applications
            }
        ]
    }
    
    # Save the converted file
    output_filename = f'daoip-5/json/CeloPG/round_{round_id}_applications_uri.json'
    with open(output_filename, 'w') as f:
        json.dump(daoip5_structure, f, indent=4)
    
    print(f"Converted {len(daoip5_applications)} applications for Round {round_id}")
    return len(daoip5_applications)

def main():
    """Main conversion function"""
    print("=== Converting CeloPG Data to DAOIP-5 Format ===")
    
    # Create grants_pool.json
    pools_count = create_grants_pool()
    
    # Convert all round application files
    round_files = [f for f in os.listdir('daoip-5/raw/CeloPG/') 
                   if f.startswith('round_') and f.endswith('.json') and f != 'roundsOnCelo.json']
    
    total_applications = 0
    for round_file in sorted(round_files):
        app_count = convert_round_applications(round_file)
        total_applications += app_count
    
    print(f"\n=== Conversion Complete ===")
    print(f"Created {pools_count} grant pools")
    print(f"Converted {len(round_files)} rounds")
    print(f"Total applications: {total_applications}")
    print(f"Files saved to: daoip-5/json/CeloPG/")

if __name__ == "__main__":
    main()