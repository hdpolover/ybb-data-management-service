#!/usr/bin/env python3
"""
YBB Data Management Service - Health Check and Performance Monitor
"""

import requests
import json
import time
import sys
import argparse
from datetime import datetime
from typing import Dict, Any, Optional

class YBBServiceMonitor:
    def __init__(self, base_url: str = "http://localhost:5000", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'YBB-Service-Monitor/1.0',
            'Accept': 'application/json'
        })
    
    def health_check(self) -> Dict[str, Any]:
        """Perform basic health check"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/health", timeout=self.timeout)
            response_time = (time.time() - start_time) * 1000
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'endpoint': '/health',
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'success': response.status_code == 200
            }
            
            if response.status_code == 200:
                try:
                    result['response_data'] = response.json()
                except:
                    result['response_data'] = response.text
            else:
                result['error'] = response.text
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'endpoint': '/health',
                'success': False,
                'error': str(e),
                'response_time_ms': 0
            }
    
    def performance_test(self, record_count: int = 100) -> Dict[str, Any]:
        """Test API performance with sample data"""
        
        # Generate test data
        test_data = [
            {
                'id': i,
                'name': f'Test User {i}',
                'email': f'user{i}@test.com',
                'status': 'active' if i % 2 == 0 else 'pending',
                'created_at': datetime.now().isoformat(),
                'score': i * 10
            }
            for i in range(1, record_count + 1)
        ]
        
        tests = {}
        
        # Test 1: Data validation
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/api/data/validate",
                json={'data': test_data},
                timeout=self.timeout
            )
            response_time = (time.time() - start_time) * 1000
            
            tests['data_validation'] = {
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'success': response.status_code == 200,
                'records_tested': record_count
            }
            
            if response.status_code == 200:
                validation_data = response.json()
                tests['data_validation']['validation_results'] = validation_data.get('data', {})
            
        except Exception as e:
            tests['data_validation'] = {
                'success': False,
                'error': str(e),
                'records_tested': record_count
            }
        
        # Test 2: Data processing
        try:
            operations = [
                {'type': 'filter', 'column': 'status', 'value': 'active'},
                {'type': 'sort', 'column': 'score', 'order': 'desc'}
            ]
            
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/api/data/process",
                json={'data': test_data, 'operations': operations},
                timeout=self.timeout
            )
            response_time = (time.time() - start_time) * 1000
            
            tests['data_processing'] = {
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'success': response.status_code == 200,
                'records_input': record_count,
                'operations': len(operations)
            }
            
            if response.status_code == 200:
                process_data = response.json()
                tests['data_processing']['records_output'] = len(process_data.get('data', []))
            
        except Exception as e:
            tests['data_processing'] = {
                'success': False,
                'error': str(e),
                'records_input': record_count
            }
        
        # Test 3: Excel export (small dataset)
        try:
            small_data = test_data[:10]  # Use smaller dataset for export test
            
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/api/export/excel",
                json={'data': small_data, 'filename': 'test_export.xlsx'},
                timeout=self.timeout
            )
            response_time = (time.time() - start_time) * 1000
            
            tests['excel_export'] = {
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'success': response.status_code == 200,
                'records_exported': len(small_data)
            }
            
            if response.status_code == 200:
                tests['excel_export']['file_size_bytes'] = len(response.content)
            
        except Exception as e:
            tests['excel_export'] = {
                'success': False,
                'error': str(e),
                'records_exported': 10
            }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'test_data_size': record_count,
            'tests': tests
        }
    
    def log_analysis(self) -> Dict[str, Any]:
        """Get recent log statistics"""
        try:
            response = self.session.get(f"{self.base_url}/api/logs/stats", timeout=self.timeout)
            
            if response.status_code == 200:
                return {
                    'timestamp': datetime.now().isoformat(),
                    'success': True,
                    'log_stats': response.json()
                }
            else:
                return {
                    'timestamp': datetime.now().isoformat(),
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            }
    
    def comprehensive_check(self, record_count: int = 100) -> Dict[str, Any]:
        """Perform comprehensive service check"""
        
        print("🔍 Performing comprehensive YBB service check...")
        print("=" * 60)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'service_url': self.base_url,
            'checks': {}
        }
        
        # Health check
        print("1. Health check...")
        health_result = self.health_check()
        results['checks']['health'] = health_result
        
        if health_result['success']:
            print(f"   ✅ Health check passed ({health_result['response_time_ms']}ms)")
        else:
            print(f"   ❌ Health check failed: {health_result.get('error', 'Unknown error')}")
            return results  # Stop if health check fails
        
        # Performance tests
        print("2. Performance tests...")
        perf_result = self.performance_test(record_count)
        results['checks']['performance'] = perf_result
        
        for test_name, test_result in perf_result['tests'].items():
            if test_result['success']:
                print(f"   ✅ {test_name}: {test_result['response_time_ms']}ms")
            else:
                print(f"   ❌ {test_name}: {test_result.get('error', 'Failed')}")
        
        # Log analysis
        print("3. Log analysis...")
        log_result = self.log_analysis()
        results['checks']['logs'] = log_result
        
        if log_result['success']:
            print("   ✅ Log analysis completed")
        else:
            print(f"   ⚠️  Log analysis failed: {log_result.get('error', 'Unknown error')}")
        
        # Overall assessment
        print("\n📊 Overall Assessment:")
        print("=" * 30)
        
        all_success = health_result['success']
        performance_success = all(test['success'] for test in perf_result['tests'].values())
        
        if all_success and performance_success:
            print("✅ Service is healthy and performing well")
            results['overall_status'] = 'healthy'
        elif all_success:
            print("⚠️  Service is healthy but has performance issues")
            results['overall_status'] = 'degraded'
        else:
            print("❌ Service has critical issues")
            results['overall_status'] = 'unhealthy'
        
        return results

def main():
    parser = argparse.ArgumentParser(description='YBB Data Management Service Monitor')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='Base URL of the YBB service (default: http://localhost:5000)')
    parser.add_argument('--timeout', type=int, default=30,
                       help='Request timeout in seconds (default: 30)')
    parser.add_argument('--records', type=int, default=100,
                       help='Number of test records for performance tests (default: 100)')
    parser.add_argument('--check', choices=['health', 'performance', 'logs', 'all'], 
                       default='all', help='Type of check to perform (default: all)')
    parser.add_argument('--json', action='store_true',
                       help='Output results in JSON format')
    parser.add_argument('--continuous', type=int, metavar='SECONDS',
                       help='Run continuously with specified interval')
    
    args = parser.parse_args()
    
    monitor = YBBServiceMonitor(args.url, args.timeout)
    
    def run_checks():
        if args.check == 'health':
            result = monitor.health_check()
        elif args.check == 'performance':
            result = monitor.performance_test(args.records)
        elif args.check == 'logs':
            result = monitor.log_analysis()
        else:  # all
            result = monitor.comprehensive_check(args.records)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if args.check != 'all':  # comprehensive_check already prints results
                print(f"\nResults for {args.check} check:")
                print("=" * 40)
                print(json.dumps(result, indent=2))
        
        return result
    
    if args.continuous:
        print(f"🔄 Running continuous monitoring every {args.continuous} seconds...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                result = run_checks()
                
                # Check if service is unhealthy
                if hasattr(result, 'get') and result.get('overall_status') == 'unhealthy':
                    print("⚠️  Service is unhealthy - consider investigation")
                
                print(f"\n⏰ Next check in {args.continuous} seconds...\n")
                time.sleep(args.continuous)
                
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
            sys.exit(0)
    else:
        result = run_checks()
        
        # Set exit code based on results
        if hasattr(result, 'get'):
            status = result.get('overall_status')
            if status == 'unhealthy':
                sys.exit(1)
            elif status == 'degraded':
                sys.exit(2)
            else:
                sys.exit(0)
        else:
            # For individual checks
            if result.get('success', False):
                sys.exit(0)
            else:
                sys.exit(1)

if __name__ == '__main__':
    main()
