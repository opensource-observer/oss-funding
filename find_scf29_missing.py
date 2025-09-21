#!/usr/bin/env python3
import pandas as pd
import json

def normalize_name(name):
    """Normalize project names for comparison"""
    name = name.lower().strip()
    # Remove common suffixes and variations
    name = name.replace(" - ", " ").replace(":", "").replace("'s", "s")
    # Handle specific variations we found
    mappings = {
        "balanced to stellar - relay 2": "balanced",
        "beans app - cards & passkeys": "beans app", 
        "bitwave enterprise payments": "bitwave",
        "borderDollar - invoice finance": "borderDollar",
        "clob dex": "clob",
        "digicus - from mvp to 1.0": "digicus",
        "globachain payment ecosystem": "globachain",
        "horizon & soroban api": "infstones",
        "houseafrikas sytemap": "sytemap",
        "lantern finance xlm expansion": "lantern finance",
        "loam - grow ambitious dapps": "loam",
        "mystic - rwa lending market": "mystic finance",
        "poma: engage-to-earn platform": "poma protocol",
        "reflector dao": "reflector",
        "soroban aiSSistant": "decentrio",
        "soroban command insights (sci)": "stellar command insights (sci)",
        "soroban full-featured indexer": "nearx - dev educational program",
        "soroban samba - educational": "sorobuilder",
        "sorostarter: soroban launchpad": "sorostarter",
        "switchly.com - bridge and dex": "switchly",
        "usdc payments for latam stores": "unalivio"
    }
    
    for long_name, short_name in mappings.items():
        if name == long_name:
            return short_name
    
    return name

def compare_projects():
    """Compare SCF 29 projects to find missing ones"""
    
    # Read CSV projects
    with open('/tmp/scf29_csv_projects.txt', 'r') as f:
        csv_projects = [line.strip() for line in f.readlines()]
    
    # Read DAOIP-5 projects  
    with open('daoip-5/json/stellar/scf_29_applications_uri.json', 'r') as f:
        daoip5_data = json.load(f)
    
    daoip5_projects = []
    for app in daoip5_data['grantPools'][0]['applications']:
        daoip5_projects.append(app['projectName'])
    
    print(f"CSV Projects: {len(csv_projects)}")
    print(f"DAOIP-5 Projects: {len(daoip5_projects)}")
    
    # Normalize and compare
    csv_normalized = {normalize_name(p): p for p in csv_projects}
    daoip5_normalized = {normalize_name(p): p for p in daoip5_projects}
    
    print(f"\nNormalized CSV: {len(csv_normalized)}")
    print(f"Normalized DAOIP-5: {len(daoip5_normalized)}")
    
    # Find missing from DAOIP-5
    missing_from_daoip5 = set(csv_normalized.keys()) - set(daoip5_normalized.keys())
    if missing_from_daoip5:
        print(f"\nMissing from DAOIP-5:")
        for norm_name in missing_from_daoip5:
            original_name = csv_normalized[norm_name]
            print(f"  - {original_name} (normalized: {norm_name})")
    
    # Find extra in DAOIP-5
    extra_in_daoip5 = set(daoip5_normalized.keys()) - set(csv_normalized.keys())
    if extra_in_daoip5:
        print(f"\nExtra in DAOIP-5:")
        for norm_name in extra_in_daoip5:
            original_name = daoip5_normalized[norm_name]
            print(f"  - {original_name} (normalized: {norm_name})")
    
    return missing_from_daoip5, csv_normalized

if __name__ == "__main__":
    missing, csv_proj = compare_projects()
    
    if missing:
        print(f"\n=== Found {len(missing)} missing project(s) ===")
        for norm_name in missing:
            print(f"Need to add: {csv_proj[norm_name]}")
    else:
        print("\n=== No missing projects found after normalization ===")
        print("The count difference may be due to naming variations only.")
