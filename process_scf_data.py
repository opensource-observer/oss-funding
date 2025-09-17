#!/usr/bin/env python3
"""
SCF Data Processor
Processes Stellar Community Fund CSV files and provides data analysis
"""

import pandas as pd
import os
import sys

def load_scf_data(filename):
    """Load and clean SCF CSV data"""
    if not os.path.exists(filename):
        print(f"Error: File {filename} not found")
        return None
    
    try:
        df = pd.read_csv(filename)
        print(f"Successfully loaded {filename}")
        print(f"Total projects: {len(df)}")
        return df
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def analyze_scf_round(df, round_name):
    """Analyze SCF round data"""
    if df is None:
        return
    
    print(f"\n=== Analysis for {round_name} ===")
    print(f"Total Projects: {len(df)}")
    
    if 'Total Awarded (USD)' in df.columns:
        # Clean the currency data
        df['Total Awarded (USD)'] = df['Total Awarded (USD)'].replace('[\$,]', '', regex=True)
        df['Total Awarded (USD)'] = pd.to_numeric(df['Total Awarded (USD)'], errors='coerce')
        
        total_awarded = df['Total Awarded (USD)'].sum()
        avg_awarded = df['Total Awarded (USD)'].mean()
        
        print(f"Total Amount Awarded: ${total_awarded:,.2f}")
        print(f"Average Award Amount: ${avg_awarded:,.2f}")
    
    if 'Status' in df.columns:
        print("\nStatus Distribution:")
        status_counts = df['Status'].value_counts()
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
    
    if 'Category (from Project)' in df.columns:
        print("\nTop Categories:")
        category_counts = df['Category (from Project)'].value_counts().head(5)
        for category, count in category_counts.items():
            print(f"  {category}: {count}")

def main():
    """Main data processing function"""
    print("SCF Data Processor Started")
    print("=" * 40)
    
    # Check for available SCF files
    scf_files = {
        'SCF #36': 'SCF_36_Projects.csv'
    }
    
    for round_name, filename in scf_files.items():
        if os.path.exists(filename):
            print(f"\nProcessing {round_name}...")
            df = load_scf_data(filename)
            analyze_scf_round(df, round_name)
        else:
            print(f"\n{round_name} data not available (file: {filename})")
    
    # Note about missing rounds
    print(f"\nNote: SCF #37 and SCF #38 are not available in the current dataset.")
    print("The latest available round is SCF #36.")
    
    print("\n" + "=" * 40)
    print("Data processing complete!")

if __name__ == "__main__":
    main()