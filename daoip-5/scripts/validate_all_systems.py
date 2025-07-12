
#!/usr/bin/env python3
"""
DAOIP-5 Comprehensive Data Quality Validation Script

This script validates all grant systems in the JSON directory and generates
a comprehensive quality report.
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from typing import Dict, List


def get_grant_systems(json_dir: str) -> List[str]:
    """Get list of all grant system directories."""
    systems = []
    for item in os.listdir(json_dir):
        system_path = os.path.join(json_dir, item)
        if os.path.isdir(system_path):
            systems.append(item)
    return sorted(systems)


def run_system_validation(system_path: str, script_path: str) -> Dict:
    """Run validation for a single grant system."""
    try:
        result = subprocess.run(
            [sys.executable, script_path, system_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # Try to load the generated report
        report_path = os.path.join(system_path, 'data_quality_report.json')
        if os.path.exists(report_path):
            with open(report_path, 'r') as f:
                report_data = json.load(f)
            return {
                'status': 'success',
                'report': report_data,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        else:
            return {
                'status': 'error',
                'error': 'Report file not generated',
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
    except subprocess.TimeoutExpired:
        return {
            'status': 'timeout',
            'error': 'Validation timed out after 5 minutes'
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


def generate_comprehensive_report(json_dir: str) -> Dict:
    """Generate comprehensive report for all grant systems."""
    script_path = os.path.join(os.path.dirname(__file__), 'validate_data_quality.py')
    systems = get_grant_systems(json_dir)
    
    comprehensive_report = {
        'timestamp': datetime.now().isoformat(),
        'total_systems': len(systems),
        'systems': {},
        'summary': {
            'successful_validations': 0,
            'failed_validations': 0,
            'total_applications': 0,
            'total_grant_pools': 0,
            'total_files': 0,
            'average_quality_score': 0,
            'systems_by_quality': {
                'excellent': [],  # 90-100
                'good': [],       # 70-89
                'fair': [],       # 50-69
                'poor': []        # <50
            }
        },
        'global_issues': {
            'critical': [],
            'schema': [],
            'data_quality': [],
            'warnings': []
        }
    }
    
    print(f"🔍 Starting comprehensive validation of {len(systems)} grant systems...")
    
    quality_scores = []
    
    for system in systems:
        system_path = os.path.join(json_dir, system)
        print(f"\n📋 Validating {system}...")
        
        validation_result = run_system_validation(system_path, script_path)
        comprehensive_report['systems'][system] = validation_result
        
        if validation_result['status'] == 'success':
            comprehensive_report['summary']['successful_validations'] += 1
            report = validation_result['report']
            
            # Aggregate statistics
            stats = report.get('statistics', {})
            comprehensive_report['summary']['total_applications'] += stats.get('total_applications', 0)
            comprehensive_report['summary']['total_grant_pools'] += stats.get('total_grant_pools', 0)
            comprehensive_report['summary']['total_files'] += stats.get('files_processed', 0)
            
            # Track quality scores
            quality_score = report.get('quality_score', 0)
            quality_scores.append(quality_score)
            
            # Categorize by quality
            if quality_score >= 90:
                comprehensive_report['summary']['systems_by_quality']['excellent'].append(system)
            elif quality_score >= 70:
                comprehensive_report['summary']['systems_by_quality']['good'].append(system)
            elif quality_score >= 50:
                comprehensive_report['summary']['systems_by_quality']['fair'].append(system)
            else:
                comprehensive_report['summary']['systems_by_quality']['poor'].append(system)
            
            # Aggregate issues
            issues = report.get('issues', {})
            for issue_type in ['critical', 'schema', 'data_quality', 'warnings']:
                system_issues = issues.get(issue_type, [])
                for issue in system_issues:
                    comprehensive_report['global_issues'][issue_type].append(f"[{system}] {issue}")
            
            print(f"   ✅ Quality Score: {quality_score}/100")
            
        else:
            comprehensive_report['summary']['failed_validations'] += 1
            print(f"   ❌ Validation failed: {validation_result.get('error', 'Unknown error')}")
    
    # Calculate average quality score
    if quality_scores:
        comprehensive_report['summary']['average_quality_score'] = sum(quality_scores) / len(quality_scores)
    
    return comprehensive_report


def save_comprehensive_report(report: Dict, json_dir: str):
    """Save comprehensive report to file."""
    report_path = os.path.join(json_dir, 'comprehensive_data_quality_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Comprehensive report saved to: {report_path}")


def print_summary(report: Dict):
    """Print a summary of the comprehensive validation."""
    summary = report['summary']
    
    print(f"\n🎯 Comprehensive Validation Summary")
    print(f"{'='*50}")
    print(f"Total Systems: {report['total_systems']}")
    print(f"Successful Validations: {summary['successful_validations']}")
    print(f"Failed Validations: {summary['failed_validations']}")
    print(f"Average Quality Score: {summary['average_quality_score']:.1f}/100")
    
    print(f"\n📊 Aggregated Statistics:")
    print(f"   Total Applications: {summary['total_applications']}")
    print(f"   Total Grant Pools: {summary['total_grant_pools']}")
    print(f"   Total Files: {summary['total_files']}")
    
    print(f"\n🏆 Systems by Quality:")
    for category, systems in summary['systems_by_quality'].items():
        if systems:
            print(f"   {category.title()}: {', '.join(systems)}")
    
    print(f"\n⚠️  Global Issues Summary:")
    for issue_type, issues in report['global_issues'].items():
        if issues:
            print(f"   {issue_type.title()}: {len(issues)} issues")
            # Show first few examples
            for issue in issues[:3]:
                print(f"     - {issue}")
            if len(issues) > 3:
                print(f"     ... and {len(issues) - 3} more")


def main():
    # Determine the JSON directory path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_dir = os.path.join(script_dir, '..', 'json')
    json_dir = os.path.abspath(json_dir)
    
    if not os.path.exists(json_dir):
        print(f"❌ Error: JSON directory not found at {json_dir}")
        sys.exit(1)
    
    print(f"🚀 Starting comprehensive validation of DAOIP-5 data")
    print(f"   JSON Directory: {json_dir}")
    
    # Generate comprehensive report
    report = generate_comprehensive_report(json_dir)
    
    # Save report
    save_comprehensive_report(report, json_dir)
    
    # Print summary
    print_summary(report)
    
    # Exit with appropriate code
    if report['summary']['failed_validations'] > 0:
        print(f"\n⚠️  Some validations failed. Check individual system reports for details.")
        sys.exit(1)
    else:
        print(f"\n✅ All validations completed successfully!")


if __name__ == "__main__":
    main()
