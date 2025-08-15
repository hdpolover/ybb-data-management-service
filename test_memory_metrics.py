#!/usr/bin/env python3
"""
Test enhanced metrics with memory tracking
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ybb_export_service import YBBExportService

def test_memory_metrics():
    # Test with memory tracking
    test_data = [
        {
            'id': i,
            'full_name': f'Memory Test User {i}',
            'email': f'memtest{i}@example.com',
            'status': 'Approved',
            'registration_date': '2025-07-27',
            'notes': 'A' * 1000  # 1KB of text per record
        } for i in range(1, 101)  # 100 records
    ]

    export_request = {
        'export_type': 'participants',
        'template': 'standard',
        'data': test_data,
        'format': 'excel'
    }

    export_service = YBBExportService()
    result = export_service.create_export(export_request)

    if result['status'] == 'success':
        data_info = result['data']
        meta_info = result['metadata']
        
        print('✅ Export with Memory Tracking:')
        print(f'   Records: {data_info["record_count"]}')
        print(f'   File Size: {data_info["file_size"]:,} bytes ({data_info["file_size_mb"]} MB)')
        print(f'   Processing Time: {meta_info["processing_time_ms"]} ms')
        print(f'   Records/Second: {meta_info["records_per_second"]}')
        
        mem_used = meta_info.get('memory_used_mb', 'N/A')
        peak_mem = meta_info.get('peak_memory_mb', 'N/A')
        efficiency = meta_info.get('memory_efficiency_kb_per_record', 'N/A')
        
        print(f'   Memory Used: {mem_used} MB')
        print(f'   Peak Memory: {peak_mem} MB')
        print(f'   Memory Efficiency: {efficiency} KB/record')
    else:
        print(f'❌ Export failed: {result.get("message")}')

if __name__ == "__main__":
    test_memory_metrics()
