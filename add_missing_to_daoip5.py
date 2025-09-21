#!/usr/bin/env python3
import json
import re
from datetime import datetime

def parse_currency_amount(amount_str):
    """Parse currency amount like '$25000.00' to float"""
    if not amount_str or amount_str == "":
        return 0.0
    # Remove $ and commas, convert to float
    clean_amount = re.sub(r'[^\d.]', '', amount_str)
    return float(clean_amount) if clean_amount else 0.0

def parse_date(date_str):
    """Convert MM/DD/YYYY to ISO format"""
    if not date_str or date_str == "":
        return "2024-12-01T00:00:00Z"
    try:
        # Parse MM/DD/YYYY format
        date_obj = datetime.strptime(date_str, "%m/%d/%Y")
        return date_obj.strftime("%Y-%m-%dT00:00:00Z")
    except:
        return "2024-12-01T00:00:00Z"

def create_daoip5_entry(project_data, round_num, app_id):
    """Convert CSV project data to DAOIP-5 format"""
    
    project_name = project_data["Submission / Project"]
    total_awarded = parse_currency_amount(project_data["Total Awarded (USD)"])
    total_paid = parse_currency_amount(project_data["Total Paid (USD)"])
    total_paid_xlm = parse_currency_amount(project_data["Total Paid (XLM)"])
    completion_pct = float(project_data.get("Tranche Completion %", 0) or 0)
    
    # Create project ID from name (convert to lowercase, replace spaces with hyphens)
    project_id_name = re.sub(r'[^a-zA-Z0-9\s-]', '', project_name.lower())
    project_id_name = re.sub(r'\s+', '-', project_id_name.strip())
    
    entry = {
        "type": "GrantApplication",
        "id": f"daoip-5:stellar:grantPool:scf_{round_num}:grantApplication:{app_id}",
        "grantPoolId": f"daoip-5:stellar:grantPool:scf_{round_num}",
        "grantPoolName": f"scf_{round_num}",
        "projectsURI": "",
        "projectId": f"daoip-5:stellar:project:{project_id_name}",
        "projectName": project_name,
        "createdAt": "2024-12-01T00:00:00Z",
        "contentURI": "",
        "status": "Awarded",
        "description": project_data.get("One-Sentence-Description", ""),
        "fundsApprovedInUSD": total_awarded
    }
    
    # Build extensions
    extensions = {
        "stellar.productsAndServices": project_data.get("Products & Services", ""),
        "stellar.successCriteria": project_data.get("Success Criteria", ""),
        "stellar.tractionEvidence": project_data.get("Traction Evidence", ""),
        "stellar.goToMarketPlan": project_data.get("Go-To-Market Plan", ""),
        "stellar.tranche1Deliverables": project_data.get("Tranche 1 - Deliverables", ""),
        "stellar.tranche2Testnet": project_data.get("Tranche 2 - Testnet", ""),
        "stellar.tranche3Mainnet": project_data.get("Tranche 3 - Mainnet", ""),
        "stellar.teamMembers": project_data.get("Team Members", ""),
        "stellar.urls": {},
        "org.stellar.communityfund.awardType": project_data.get("Award Type", "Build"),
        "org.stellar.communityfund.fundsPaid": [],
        "org.stellar.communityfund.latestTranche": project_data.get("Latest Tranche (from Payments)", ""),
        "org.stellar.communityfund.category": project_data.get("Category (from Project)", "Applications")
    }
    
    # Add URLs if available
    if project_data.get("Website"):
        extensions["stellar.urls"]["website"] = project_data["Website"]
    if project_data.get("Code"):
        extensions["stellar.urls"]["codeRepository"] = project_data["Code"]
    if project_data.get("Video"):
        extensions["stellar.urls"]["videoURL"] = project_data["Video"]
    if project_data.get("Technical Architecture"):
        extensions["stellar.technicalArchitecture"] = project_data["Technical Architecture"]
    if project_data.get("Pitch Deck (from Project)"):
        extensions["stellar.urls"]["pitchDeck"] = project_data["Pitch Deck (from Project)"]
    
    # Add social media if available
    social_media = {}
    if project_data.get("LinkedIn (from Project)"):
        social_media["linkedIn"] = project_data["LinkedIn (from Project)"]
    if project_data.get("X (from Project)"):
        social_media["twitter"] = project_data["X (from Project)"]
    if project_data.get("Discord (from Project)"):
        social_media["discord"] = project_data["Discord (from Project)"]
    
    if social_media:
        extensions["stellar.socialMedia"] = social_media
    
    # Add payment information
    if total_paid > 0:
        funds_paid = [{"amount": total_paid, "denomination": "USD"}]
        if total_paid_xlm > 0:
            funds_paid.append({"amount": total_paid_xlm, "denomination": "XLM"})
        extensions["org.stellar.communityfund.fundsPaid"] = funds_paid
    
    # Add payment date if available
    if project_data.get("Most Recent Payment Date"):
        payment_date = parse_date(project_data["Most Recent Payment Date"])
        extensions["org.stellar.communityfund.mostRecentPaymentDate"] = payment_date
    
    entry["extensions"] = extensions
    
    # Add completion percentage if available
    if completion_pct > 0:
        entry["completionPercentage"] = completion_pct
    
    return entry

# Load project data
print("=== Creating DAOIP-5 Entries ===")

with open('/tmp/stellar_dune_data.json', 'r') as f:
    stellar_dune_data = json.load(f)

with open('/tmp/greep_pos_data.json', 'r') as f:
    greep_pos_data = json.load(f)

# Create DAOIP-5 entries
stellar_dune_entry = create_daoip5_entry(stellar_dune_data, 35, 21)
greep_pos_entry = create_daoip5_entry(greep_pos_data, 34, 17)

# Save entries
with open('/tmp/stellar_dune_daoip5.json', 'w') as f:
    json.dump(stellar_dune_entry, f, indent=2)

with open('/tmp/greep_pos_daoip5.json', 'w') as f:
    json.dump(greep_pos_entry, f, indent=2)

print("Stellar DeFi Dune Dashboards DAOIP-5 entry created")
print(f"Project ID: {stellar_dune_entry['projectId']}")
print(f"Funding: ${stellar_dune_entry['fundsApprovedInUSD']}")

print("\nGreep POS DAOIP-5 entry created")
print(f"Project ID: {greep_pos_entry['projectId']}")
print(f"Funding: ${greep_pos_entry['fundsApprovedInUSD']}")

print("\n=== DAOIP-5 Entries Ready for Addition ===")