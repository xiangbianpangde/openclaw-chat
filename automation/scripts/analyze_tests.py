#!/usr/bin/env python3
"""
OpenClaw IM Test Report Analyzer
Analyzes test results and generates fix recommendations
"""

import os
import sys
import json
import yaml
from datetime import datetime
from pathlib import Path

def load_config():
    """Load gateway configuration"""
    config_path = Path(__file__).parent / 'config' / 'gateway.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def analyze_test_report(report_path):
    """Analyze HTML test report and extract results"""
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'errors': [],
        'timestamp': datetime.now().isoformat()
    }
    
    if not os.path.exists(report_path):
        return results
    
    try:
        with open(report_path, 'r') as f:
            content = f.read()
            
        # Simple parsing of pytest-html report
        if '"pass":' in content:
            import re
            pass_match = re.search(r'"pass":\s*(\d+)', content)
            fail_match = re.search(r'"fail":\s*(\d+)', content)
            
            if pass_match:
                results['passed'] = int(pass_match.group(1))
            if fail_match:
                results['failed'] = int(fail_match.group(1))
            
            results['total'] = results['passed'] + results['failed']
            
        # Check for specific error patterns
        error_patterns = [
            ('timeout', 'Timeout error - consider increasing wait times'),
            ('connection', 'Connection error - check gateway configuration'),
            ('element not found', 'UI element not found - app structure may have changed'),
            ('assertion', 'Assertion failed - functionality not working as expected'),
        ]
        
        for pattern, recommendation in error_patterns:
            if pattern.lower() in content.lower():
                results['errors'].append({
                    'type': pattern,
                    'recommendation': recommendation
                })
                
    except Exception as e:
        results['errors'].append({
            'type': 'parse_error',
            'message': str(e)
        })
    
    return results

def generate_fix_recommendations(results):
    """Generate fix recommendations based on test results"""
    recommendations = []
    
    if results['failed'] > 0:
        recommendations.append({
            'priority': 'high',
            'action': 'Review failed tests',
            'details': f"{results['failed']} tests failed. Check test report for details."
        })
    
    for error in results.get('errors', []):
        if error['type'] == 'timeout':
            recommendations.append({
                'priority': 'medium',
                'action': 'Increase timeout values',
                'details': error.get('recommendation', 'Consider increasing wait times in tests')
            })
        elif error['type'] == 'connection':
            recommendations.append({
                'priority': 'high',
                'action': 'Check gateway configuration',
                'details': 'Verify WebSocket gateway URL and token are correct'
            })
    
    return recommendations

def main():
    """Main entry point"""
    config = load_config()
    
    # Find latest report
    reports_dir = Path(__file__).parent / 'reports'
    reports = list(reports_dir.glob('test_report_*.html'))
    
    if not reports:
        print("No test reports found")
        return
    
    latest_report = max(reports, key=os.path.getctime)
    print(f"Analyzing: {latest_report}")
    
    results = analyze_test_report(str(latest_report))
    recommendations = generate_fix_recommendations(results)
    
    print(f"\n=== Test Results ===")
    print(f"Total: {results['total']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    
    if recommendations:
        print(f"\n=== Recommendations ===")
        for rec in recommendations:
            print(f"[{rec['priority'].upper()}] {rec['action']}: {rec['details']}")
    
    # Save analysis results
    analysis_file = reports_dir / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(analysis_file, 'w') as f:
        json.dump({
            'results': results,
            'recommendations': recommendations
        }, f, indent=2)
    
    print(f"\nAnalysis saved to: {analysis_file}")
    
    # Return exit code based on results
    sys.exit(0 if results['failed'] == 0 else 1)

if __name__ == '__main__':
    main()
