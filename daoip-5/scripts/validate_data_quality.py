
#!/usr/bin/env python3
"""
DAOIP-5 Data Quality Validation Script

This script validates JSON files against the DAOIP-5 schema and generates
quality reports for individual grant systems.
"""

import json
import os
import sys
import yaml
import re
from datetime import datetime
from typing import Dict, List, Any, Tuple
from urllib.parse import urlparse


class DataQualityValidator:
    def __init__(self, system_path: str):
        self.system_path = system_path
        self.system_name = os.path.basename(system_path)
        self.issues = {
            'critical': [],
            'schema': [],
            'data_quality': [],
            'warnings': []
        }
        self.stats = {
            'total_applications': 0,
            'total_grant_pools': 0,
            'files_processed': 0,
            'valid_applications': 0
        }
        self.field_mapping = self.load_field_mapping()
    
    def load_field_mapping(self) -> Dict:
        """Load field mapping configuration from YAML file."""
        mapping_file = os.path.join(self.system_path, 'field_mapping.yaml')
        if os.path.exists(mapping_file):
            with open(mapping_file, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def validate_date_format(self, date_str: str, field_name: str) -> bool:
        """Validate if date string is in ISO8601 format."""
        if not date_str:
            return True  # null dates are acceptable
        
        iso8601_patterns = [
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$',
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$',
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$'
        ]
        
        for pattern in iso8601_patterns:
            if re.match(pattern, date_str):
                return True
        
        self.issues['critical'].append(f"Invalid date format in {field_name}: {date_str}")
        return False
    
    def validate_url(self, url: str, field_name: str) -> bool:
        """Validate URL format."""
        if not url:
            return True  # null URLs are acceptable
        
        if url in ["URL not available", "Content URL not available", "not available"]:
            self.issues['data_quality'].append(f"Placeholder URL in {field_name}: {url}")
            return False
        
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            self.issues['data_quality'].append(f"Invalid URL format in {field_name}: {url}")
            return False
        
        return True
    
    def validate_schema_consistency(self, data: Dict) -> bool:
        """Check for schema consistency issues."""
        valid = True
        
        # Check root level field naming
        if 'grant_pools' in data and 'grantPools' not in data:
            self.issues['schema'].append("Uses 'grant_pools' instead of 'grantPools' at root level")
            valid = False
        
        return valid
    
    def validate_application(self, app: Dict, pool_id: str) -> bool:
        """Validate individual application data."""
        valid = True
        app_id = app.get('id', 'unknown')
        
        # Required fields check
        required_fields = ['type', 'id', 'grantPoolId', 'projectName', 'createdAt']
        for field in required_fields:
            if field not in app or app[field] is None:
                self.issues['critical'].append(f"Missing required field '{field}' in application {app_id}")
                valid = False
        
        # Check for placeholder values
        if app.get('projectName') in ['Unnamed Project', 'Unknown', '']:
            self.issues['data_quality'].append(f"Placeholder project name in application {app_id}: {app.get('projectName')}")
        
        if app.get('projectId') in ['unknown-project', 'Unknown', '']:
            self.issues['data_quality'].append(f"Placeholder project ID in application {app_id}: {app.get('projectId')}")
        
        # Validate dates
        if 'createdAt' in app:
            self.validate_date_format(app['createdAt'], f"application {app_id} createdAt")
        
        # Validate URLs
        for url_field in ['projectsURI', 'contentURI']:
            if url_field in app:
                self.validate_url(app[url_field], f"application {app_id} {url_field}")
        
        # Validate funds
        for funds_field in ['fundsAsked', 'fundsApproved']:
            if funds_field in app and isinstance(app[funds_field], list):
                for i, fund in enumerate(app[funds_field]):
                    if isinstance(fund, dict):
                        amount = fund.get('amount')
                        if amount == "Unknown":
                            self.issues['critical'].append(f"String 'Unknown' found in {funds_field}[{i}].amount for application {app_id} - should be null")
                            valid = False
                        elif amount is not None and not isinstance(amount, (int, float)):
                            self.issues['data_quality'].append(f"Invalid amount type in {funds_field}[{i}] for application {app_id}: {type(amount)}")
        
        return valid
    
    def validate_file(self, file_path: str) -> Dict:
        """Validate a single JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return {'error': f"JSON decode error: {e}", 'valid': False}
        except Exception as e:
            return {'error': f"File read error: {e}", 'valid': False}
        
        file_result = {
            'file': os.path.basename(file_path),
            'valid': True,
            'applications_count': 0,
            'grant_pools_count': 0
        }
        
        # Validate schema consistency
        self.validate_schema_consistency(data)
        
        # Process grant pools
        pools_key = 'grantPools' if 'grantPools' in data else 'grant_pools'
        if pools_key in data:
            for pool in data[pools_key]:
                self.stats['total_grant_pools'] += 1
                file_result['grant_pools_count'] += 1
                
                # Validate applications if present
                if 'applications' in pool:
                    for app in pool['applications']:
                        self.stats['total_applications'] += 1
                        file_result['applications_count'] += 1
                        
                        if self.validate_application(app, pool.get('id', 'unknown')):
                            self.stats['valid_applications'] += 1
        
        self.stats['files_processed'] += 1
        return file_result
    
    def generate_report(self) -> Dict:
        """Generate validation report for the grant system."""
        files_results = []
        
        # Process all JSON files in the system directory
        for filename in os.listdir(self.system_path):
            if filename.endswith('.json') and filename != 'field_mapping.yaml':
                file_path = os.path.join(self.system_path, filename)
                result = self.validate_file(file_path)
                files_results.append(result)
        
        # Calculate quality score
        total_issues = sum(len(issues) for issues in self.issues.values())
        quality_score = max(0, 100 - (total_issues * 5))  # Deduct 5 points per issue
        
        report = {
            'system_name': self.system_name,
            'timestamp': datetime.now().isoformat(),
            'quality_score': quality_score,
            'statistics': self.stats,
            'files': files_results,
            'issues': self.issues,
            'field_mapping': self.field_mapping
        }
        
        return report
    
    def save_report(self, report: Dict):
        """Save validation report to file."""
        report_path = os.path.join(self.system_path, 'data_quality_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Report saved to: {report_path}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_data_quality.py <grant_system_path>")
        print("Example: python validate_data_quality.py ../json/arbitrumfoundation")
        sys.exit(1)
    
    system_path = sys.argv[1]
    
    if not os.path.exists(system_path):
        print(f"❌ Error: Path {system_path} does not exist")
        sys.exit(1)
    
    print(f"🔍 Validating data quality for: {os.path.basename(system_path)}")
    
    validator = DataQualityValidator(system_path)
    report = validator.generate_report()
    validator.save_report(report)
    
    # Print summary
    print(f"\n📊 Validation Summary:")
    print(f"   Quality Score: {report['quality_score']}/100")
    print(f"   Files Processed: {report['statistics']['files_processed']}")
    print(f"   Total Applications: {report['statistics']['total_applications']}")
    print(f"   Valid Applications: {report['statistics']['valid_applications']}")
    print(f"   Critical Issues: {len(report['issues']['critical'])}")
    print(f"   Schema Issues: {len(report['issues']['schema'])}")
    print(f"   Data Quality Issues: {len(report['issues']['data_quality'])}")
    print(f"   Warnings: {len(report['issues']['warnings'])}")
    
    if report['issues']['critical']:
        print(f"\n🚨 Critical Issues:")
        for issue in report['issues']['critical'][:5]:  # Show first 5
            print(f"   - {issue}")
        if len(report['issues']['critical']) > 5:
            print(f"   ... and {len(report['issues']['critical']) - 5} more")


if __name__ == "__main__":
    main()
