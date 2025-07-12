
#!/usr/bin/env python3
"""
DAOIP-5 Data Quality Check Runner

This script provides various data quality check operations for the DAOIP-5 system.
Can be run manually or as part of automated workflows.
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path


def get_script_dir():
    """Get the directory where this script is located."""
    return Path(__file__).parent


def run_command(command, cwd=None):
    """Run a command and return success status."""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {command}")
        print(f"Exit code: {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False


def validate_single_system(system_path):
    """Validate a single grant system."""
    script_dir = get_script_dir()
    validate_script = script_dir / "validate_data_quality.py"
    
    print(f"🔍 Validating system: {system_path}")
    command = f"python3 {validate_script} {system_path}"
    return run_command(command)


def validate_all_systems():
    """Validate all grant systems."""
    script_dir = get_script_dir()
    validate_script = script_dir / "validate_all_systems.py"
    
    print("🔍 Running comprehensive validation of all systems...")
    command = f"python3 {validate_script}"
    return run_command(command, cwd=script_dir)


def apply_critical_fixes(target="all"):
    """Apply critical fixes to systems."""
    script_dir = get_script_dir()
    fix_script = script_dir / "fix_critical_issues.py"
    json_dir = script_dir.parent / "json"
    
    if target == "all":
        print("🔧 Applying critical fixes to all systems...")
        command = f"python3 {fix_script} {json_dir} all"
    else:
        print(f"🔧 Applying critical fixes to: {target}")
        command = f"python3 {fix_script} {target}"
    
    return run_command(command, cwd=script_dir)


def convert_csv_to_json(funder_path):
    """Convert CSV data to DAOIP-5 JSON format."""
    script_dir = get_script_dir()
    convert_script = script_dir / "CSV-to-JSON.py"
    
    print(f"📊 Converting CSV to JSON for: {funder_path}")
    command = f"python3 {convert_script} --path {funder_path}"
    return run_command(command)


def check_system_structure(funder_path):
    """Check if a funder directory has the required structure."""
    funder_path = Path(funder_path)
    
    if not funder_path.exists():
        print(f"❌ Path does not exist: {funder_path}")
        return False
    
    # Check for YAML file
    yaml_files = list(funder_path.glob("*.yaml"))
    if not yaml_files:
        print(f"❌ No YAML file found in {funder_path}")
        return False
    
    # Check for uploads directory
    uploads_dir = funder_path / "uploads"
    if not uploads_dir.exists():
        print(f"❌ No uploads directory found in {funder_path}")
        return False
    
    # Check for CSV files in uploads
    csv_files = list(uploads_dir.glob("*.csv"))
    if not csv_files:
        print(f"❌ No CSV files found in {uploads_dir}")
        return False
    
    print(f"✅ Valid structure found in {funder_path}")
    print(f"   YAML file: {yaml_files[0].name}")
    print(f"   CSV files: {len(csv_files)} found")
    return True


def process_new_funder(funder_path):
    """Process a new funder directory completely."""
    funder_path = Path(funder_path).resolve()
    
    print(f"🚀 Processing new funder: {funder_path}")
    
    # Check structure
    if not check_system_structure(funder_path):
        return False
    
    # Convert CSV to JSON
    if not convert_csv_to_json(funder_path):
        return False
    
    # Get system name and validate
    system_name = funder_path.name
    json_system_path = get_script_dir().parent / "json" / system_name
    
    if json_system_path.exists():
        if not validate_single_system(json_system_path):
            print("⚠️ Validation completed with issues - check report")
        
        # Apply fixes if needed
        apply_critical_fixes(json_system_path)
        
        print(f"✅ Successfully processed funder: {system_name}")
        return True
    else:
        print(f"❌ JSON files not generated for: {system_name}")
        return False


def main():
    parser = argparse.ArgumentParser(description='DAOIP-5 Data Quality Check Runner')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Validate single system
    validate_parser = subparsers.add_parser('validate', help='Validate a single grant system')
    validate_parser.add_argument('system_path', help='Path to the grant system JSON directory')
    
    # Validate all systems
    subparsers.add_parser('validate-all', help='Validate all grant systems')
    
    # Apply fixes
    fix_parser = subparsers.add_parser('fix', help='Apply critical fixes')
    fix_parser.add_argument('target', nargs='?', default='all', 
                           help='Target to fix (path or "all")')
    
    # Convert CSV to JSON
    convert_parser = subparsers.add_parser('convert', help='Convert CSV to DAOIP-5 JSON')
    convert_parser.add_argument('funder_path', help='Path to the funder directory')
    
    # Process new funder
    process_parser = subparsers.add_parser('process', help='Process a new funder completely')
    process_parser.add_argument('funder_path', help='Path to the funder directory')
    
    # Check structure
    check_parser = subparsers.add_parser('check', help='Check funder directory structure')
    check_parser.add_argument('funder_path', help='Path to the funder directory')
    
    # Full pipeline
    subparsers.add_parser('full-check', help='Run complete data quality pipeline')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    success = True
    
    if args.command == 'validate':
        success = validate_single_system(args.system_path)
    elif args.command == 'validate-all':
        success = validate_all_systems()
    elif args.command == 'fix':
        success = apply_critical_fixes(args.target)
    elif args.command == 'convert':
        success = convert_csv_to_json(args.funder_path)
    elif args.command == 'process':
        success = process_new_funder(args.funder_path)
    elif args.command == 'check':
        success = check_system_structure(args.funder_path)
    elif args.command == 'full-check':
        print("🚀 Running full data quality pipeline...")
        success = (
            validate_all_systems() and
            apply_critical_fixes() and
            validate_all_systems()  # Re-validate after fixes
        )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
