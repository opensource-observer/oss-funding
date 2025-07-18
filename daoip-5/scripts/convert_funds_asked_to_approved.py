
#!/usr/bin/env python3
"""
Convert fundsAsked to fundsApproved Script

This script converts fundsAsked to fundsApproved based on system-specific patterns:
- Stellar, Octant, Arbitrum, Optimism (except grants_season_1): fundsAsked USD → fundsApprovedInUSD (integer)
- CLRFund: fundsAsked DAI → fundsApproved + fundsApprovedInUSD
- DAO Drops: fundsAsked USD → fundsApprovedInUSD (integer, not object)
"""

import json
import os
import sys
from pathlib import Path


def create_backup(file_path):
    """Create a backup of the original file."""
    backup_path = f"{file_path}.backup"
    with open(file_path, 'r', encoding='utf-8') as original:
        with open(backup_path, 'w', encoding='utf-8') as backup:
            backup.write(original.read())
    print(f"  📁 Backup created: {backup_path}")


def handle_stellar_octant_arbitrum_optimism(app, grant_system_name, file_name):
    """Handle Stellar, Octant, Arbitrum, and Optimism (except grants_season_1)."""
    # Skip optimism grants_season_1
    if grant_system_name == 'optimism' and 'grants_season_1' in file_name:
        return False
    
    changes_made = False
    
    if 'fundsAsked' in app and app['fundsAsked']:
        funds_asked = app['fundsAsked'][0]
        if funds_asked.get('denomination') == 'USD':
            # Convert to integer and add as fundsApprovedInUSD
            usd_amount = int(funds_asked.get('amount', 0))
            app['fundsApprovedInUSD'] = usd_amount
            changes_made = True
            print(f"    💰 Added fundsApprovedInUSD: {usd_amount}")
        
        # Remove fundsAsked
        del app['fundsAsked']
        changes_made = True
    
    return changes_made


def handle_clrfund(app):
    """Handle CLRFund specific conversion."""
    changes_made = False
    
    if 'fundsAsked' in app and app['fundsAsked']:
        funds_asked_data = app['fundsAsked']
        
        # Move fundsAsked to fundsApproved
        app['fundsApproved'] = funds_asked_data
        changes_made = True
        print(f"    ✅ Moved fundsAsked to fundsApproved")
        
        # Add fundsApprovedInUSD (assuming DAI ≈ USD)
        if funds_asked_data and funds_asked_data[0].get('amount') is not None:
            usd_amount = int(funds_asked_data[0].get('amount', 0))
            app['fundsApprovedInUSD'] = usd_amount
            changes_made = True
            print(f"    💰 Added fundsApprovedInUSD: {usd_amount}")
        
        # Remove fundsAsked
        del app['fundsAsked']
        changes_made = True
    
    return changes_made


def handle_dao_drops(app):
    """Handle DAO Drops specific conversion."""
    changes_made = False
    
    if 'fundsAsked' in app and app['fundsAsked']:
        funds_asked = app['fundsAsked'][0]
        if funds_asked.get('denomination') == 'USD':
            # Convert to integer and add as fundsApprovedInUSD (not an object)
            usd_amount = int(funds_asked.get('amount', 0))
            app['fundsApprovedInUSD'] = usd_amount
            changes_made = True
            print(f"    💰 Added fundsApprovedInUSD: {usd_amount}")
        
        # Remove fundsAsked
        del app['fundsAsked']
        changes_made = True
    
    return changes_made


def update_applications_file(file_path, grant_system_name):
    """Update applications JSON file based on grant system specific patterns."""
    print(f"  🔄 Processing applications file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create backup
        create_backup(file_path)
        
        changes_made = False
        file_name = os.path.basename(file_path)
        
        # Update grantPools array
        grant_pools = data.get('grantPools', [])
        
        for pool in grant_pools:
            applications = pool.get('applications', [])
            for app in applications:
                app_id = app.get('id', 'unknown')
                
                # Handle different systems
                if grant_system_name in ['stellar', 'octant-golemfoundation', 'arbitrumfoundation', 'optimism']:
                    if handle_stellar_octant_arbitrum_optimism(app, grant_system_name, file_name):
                        changes_made = True
                        print(f"    ✅ Processed {grant_system_name} application {app_id}")
                
                elif grant_system_name == 'clrfund':
                    if handle_clrfund(app):
                        changes_made = True
                        print(f"    ✅ Processed CLRFund application {app_id}")
                
                elif grant_system_name == 'dao-drops-dorgtech':
                    if handle_dao_drops(app):
                        changes_made = True
                        print(f"    ✅ Processed DAO Drops application {app_id}")
        
        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"  💾 Saved changes to {file_path}")
        else:
            print(f"  ✨ No changes needed for {file_path}")
            
        return changes_made
        
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False


def process_grant_system(system_path):
    """Process a single grant system directory."""
    system_name = system_path.name
    print(f"\n🚀 Processing grant system: {system_name}")
    
    total_changes = 0
    files_processed = 0
    
    # Process all JSON files in the system directory
    for json_file in system_path.glob("*.json"):
        if json_file.name.endswith('.backup'):
            continue  # Skip backup files
        
        # Skip grants_pool.json as it doesn't contain applications
        if json_file.name == 'grants_pool.json':
            continue
            
        files_processed += 1
        
        # Process applications files
        if update_applications_file(json_file, system_name):
            total_changes += 1
    
    print(f"✅ Completed {system_name}: {files_processed} files processed, {total_changes} files modified")
    return total_changes


def main():
    """Main function to process all grant systems."""
    script_dir = Path(__file__).parent
    json_dir = script_dir.parent / "json"
    
    if not json_dir.exists():
        print(f"❌ JSON directory not found: {json_dir}")
        sys.exit(1)
    
    print("🎯 Convert fundsAsked to fundsApproved (System-Specific)")
    print("=" * 60)
    print("System-specific conversion patterns:")
    print("• Stellar/Octant/Arbitrum/Optimism*: fundsAsked USD → fundsApprovedInUSD (int)")
    print("• CLRFund: fundsAsked DAI → fundsApproved + fundsApprovedInUSD (int)")
    print("• DAO Drops: fundsAsked USD → fundsApprovedInUSD (int)")
    print("* Optimism grants_season_1 is excluded")
    print("=" * 60)
    
    total_systems = 0
    total_changes = 0
    
    # Process each grant system directory
    for system_dir in json_dir.iterdir():
        if system_dir.is_dir() and not system_dir.name.startswith('.'):
            total_systems += 1
            changes = process_grant_system(system_dir)
            total_changes += changes
    
    print("\n" + "=" * 60)
    print(f"🎉 Funding Data Conversion Complete!")
    print(f"📊 Summary:")
    print(f"   • Grant systems processed: {total_systems}")
    print(f"   • Files modified: {total_changes}")
    print(f"   • Backup files created for safety")
    print("=" * 60)
    
    if total_changes > 0:
        print("\n💡 Next steps:")
        print("   1. Review the changes in modified files")
        print("   2. Run data quality validation: python3 run_data_quality_check.py validate-all")


if __name__ == "__main__":
    main()
