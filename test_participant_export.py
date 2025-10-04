"""
Test Participant Export Functionality
Test the new participant export with various filters and scenarios
"""
import os
import sys
from dotenv import load_dotenv
import requests
import json
import time

# Load environment
load_dotenv()

def test_participant_export():
    """Test participant export with various scenarios"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🔍 Testing Participant Export Functionality")
    print("=" * 60)
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Basic Export - Program 2 (Standard Template)",
            "payload": {
                "program_id": 2,
                "template": "standard",
                "filters": {},
                "filename": "test_program_2_standard"
            }
        },
        {
            "name": "Filtered Export - Self Funded Only",
            "payload": {
                "program_id": 2,
                "template": "basic",
                "filters": {
                    "category": ["self_funded"]
                },
                "filename": "test_self_funded_only"
            }
        },
        {
            "name": "Form Status Filter - Submitted Only",
            "payload": {
                "program_id": 2,
                "template": "detailed",
                "filters": {
                    "form_status": [2]  # Submitted
                },
                "filename": "test_submitted_only",
                "force_chunking": True,
                "chunk_size": 2000
            }
        },
        {
            "name": "Date Range Filter - April 2024",
            "payload": {
                "program_id": 2,
                "template": "standard",
                "filters": {
                    "created_at": {
                        "min": "2024-04-01",
                        "max": "2024-04-30"
                    }
                },
                "filename": "test_april_2024"
            }
        },
        {
            "name": "With Essays Filter",
            "payload": {
                "program_id": 2,
                "template": "detailed",
                "filters": {
                    "with_essay": True
                },
                "filename": "test_with_essays_only"
            }
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📊 Test {i}: {scenario['name']}")
        print("-" * 50)
        
        try:
            # First, get count to see what we're working with
            count_payload = {
                "export_type": "participants",
                "filters": scenario["payload"]["filters"].copy()
            }
            count_payload["filters"]["program_id"] = scenario["payload"]["program_id"]
            
            print("   Getting record count...")
            count_response = requests.post(
                f"{base_url}/api/ybb/db/export/count",
                json=count_payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if count_response.status_code == 200:
                count_data = count_response.json()
                total_records = count_data.get("total_records", 0)
                print(f"   📈 Expected records: {total_records:,}")
                
                if total_records == 0:
                    print("   ⚠️ No records found for this filter combination, skipping export test")
                    results.append({
                        "scenario": scenario["name"],
                        "status": "skipped",
                        "reason": "no_records"
                    })
                    continue
            else:
                print(f"   ❌ Count request failed: {count_response.status_code}")
                continue
            
            # Perform the actual export
            print("   Starting export...")
            start_time = time.time()
            
            response = requests.post(
                f"{base_url}/api/ybb/db/export/participants",
                json=scenario["payload"],
                headers={"Content-Type": "application/json"},
                timeout=120
            )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("status") == "success":
                    data = result.get("data", {})
                    metrics = result.get("performance_metrics", {})
                    
                    print(f"   ✅ Export successful!")
                    print(f"   📄 Export ID: {data.get('export_id')}")
                    print(f"   📊 Records processed: {data.get('record_count') or data.get('total_records', 0):,}")
                    print(f"   ⏱️ Processing time: {metrics.get('total_processing_time_seconds', elapsed_time):.2f}s")
                    print(f"   🚀 Throughput: {metrics.get('total_records_per_second') or metrics.get('records_per_second', 0):,.0f} rec/s")
                    
                    if result.get("export_strategy") == "multi_file":
                        print(f"   📁 Files created: {data.get('total_files')}")
                        print(f"   📦 Archive size: {data.get('archive_info', {}).get('compressed_size', 0) / 1024 / 1024:.1f} MB")
                    else:
                        print(f"   📄 File size: {data.get('file_size_mb', 0):.1f} MB")
                    
                    results.append({
                        "scenario": scenario["name"],
                        "status": "success",
                        "records": data.get('record_count') or data.get('total_records', 0),
                        "time": metrics.get('total_processing_time_seconds', elapsed_time),
                        "throughput": metrics.get('total_records_per_second') or metrics.get('records_per_second', 0),
                        "export_id": data.get('export_id')
                    })
                    
                else:
                    print(f"   ❌ Export failed: {result.get('message', 'Unknown error')}")
                    results.append({
                        "scenario": scenario["name"],
                        "status": "failed",
                        "error": result.get('message', 'Unknown error')
                    })
            
            else:
                print(f"   ❌ Request failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error details: {error_data.get('message', 'Unknown error')}")
                except:
                    print(f"   Error response: {response.text}")
                
                results.append({
                    "scenario": scenario["name"],
                    "status": "failed",
                    "error": f"HTTP {response.status_code}"
                })
        
        except Exception as e:
            print(f"   ❌ Exception occurred: {str(e)}")
            results.append({
                "scenario": scenario["name"],
                "status": "error",
                "error": str(e)
            })
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] in ["failed", "error"]]
    skipped = [r for r in results if r["status"] == "skipped"]
    
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"⚠️ Skipped: {len(skipped)}")
    
    if successful:
        print(f"\n🏆 Performance Summary:")
        total_records = sum(r.get("records", 0) for r in successful)
        avg_throughput = sum(r.get("throughput", 0) for r in successful) / len(successful)
        print(f"   Total records processed: {total_records:,}")
        print(f"   Average throughput: {avg_throughput:,.0f} records/second")
    
    if failed:
        print(f"\n❌ Failed Tests:")
        for result in failed:
            print(f"   - {result['scenario']}: {result.get('error', 'Unknown error')}")
    
    print(f"\n🎯 Result: {len(successful)}/{len(results)} tests passed")
    
    return len(successful) == len(results) - len(skipped)

def test_program_availability():
    """Check which programs have participants"""
    try:
        print("\n🔍 Checking available programs...")
        
        # Simple query to get program stats
        response = requests.post(
            "http://127.0.0.1:5000/api/ybb/db/export/count",
            json={"export_type": "participants", "filters": {}},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            total = result.get("total_records", 0)
            print(f"   Total participants across all programs: {total:,}")
        
    except Exception as e:
        print(f"   Error checking programs: {str(e)}")

if __name__ == "__main__":
    print("🧪 YBB Participant Export Test Suite")
    print("=" * 80)
    
    # Check if server is running
    try:
        response = requests.get("http://127.0.0.1:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server health check failed")
            exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        exit(1)
    
    test_program_availability()
    success = test_participant_export()
    
    print(f"\n{'='*80}")
    if success:
        print("🎉 All tests completed successfully!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    print("=" * 80)