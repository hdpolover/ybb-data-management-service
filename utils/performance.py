"""
Performance optimization utilities for large dataset processing
"""
import gc
import psutil
import logging
from functools import wraps
import time

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor and optimize performance for large dataset operations"""
    
    @staticmethod
    def monitor_memory_usage(func):
        """Decorator to monitor memory usage of functions"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get initial memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # Get final memory usage
                final_memory = process.memory_info().rss / 1024 / 1024  # MB
                execution_time = time.time() - start_time
                
                logger.info(f"{func.__name__} - Memory: {initial_memory:.1f}MB → {final_memory:.1f}MB "
                           f"(+{final_memory - initial_memory:.1f}MB), Time: {execution_time:.2f}s")
                
                return result
                
            except Exception as e:
                final_memory = process.memory_info().rss / 1024 / 1024  # MB
                execution_time = time.time() - start_time
                
                logger.error(f"{func.__name__} failed - Memory: {initial_memory:.1f}MB → {final_memory:.1f}MB, "
                           f"Time: {execution_time:.2f}s, Error: {str(e)}")
                raise
                
        return wrapper
    
    @staticmethod
    def get_memory_usage():
        """Get current memory usage"""
        process = psutil.Process()
        return {
            'rss': process.memory_info().rss / 1024 / 1024,  # MB
            'vms': process.memory_info().vms / 1024 / 1024,  # MB
            'percent': process.memory_percent()
        }
    
    @staticmethod
    def check_memory_limit(limit_mb=1000):
        """Check if memory usage exceeds limit"""
        usage = PerformanceMonitor.get_memory_usage()
        if usage['rss'] > limit_mb:
            logger.warning(f"Memory usage ({usage['rss']:.1f}MB) exceeds limit ({limit_mb}MB)")
            return False
        return True
    
    @staticmethod
    def force_garbage_collection():
        """Force garbage collection to free memory"""
        gc.collect()
        logger.debug("Forced garbage collection")

class ChunkProcessor:
    """Utility class for processing data in chunks"""
    
    @staticmethod
    def get_optimal_chunk_size(total_records, available_memory_mb=500):
        """Calculate optimal chunk size based on available memory"""
        # Estimate memory per record (rough calculation)
        estimated_memory_per_record = 0.001  # 1KB per record (adjust based on your data)
        
        max_records_in_memory = int(available_memory_mb / estimated_memory_per_record)
        
        # Use smaller chunks for very large datasets
        if total_records > 100000:
            optimal_size = min(1000, max_records_in_memory)
        elif total_records > 50000:
            optimal_size = min(2000, max_records_in_memory)
        elif total_records > 10000:
            optimal_size = min(5000, max_records_in_memory)
        else:
            optimal_size = total_records
        
        logger.info(f"Optimal chunk size for {total_records} records: {optimal_size}")
        return optimal_size
    
    @staticmethod
    def should_use_chunked_processing(data_size, memory_threshold_mb=100):
        """Determine if chunked processing should be used"""
        estimated_memory = data_size * 0.001  # Rough estimate: 1KB per record
        return estimated_memory > memory_threshold_mb

# Performance configuration
PERFORMANCE_CONFIG = {
    'MAX_MEMORY_MB': 1000,  # Maximum memory usage before warning
    'CHUNK_SIZE_SMALL': 1000,
    'CHUNK_SIZE_MEDIUM': 2000,
    'CHUNK_SIZE_LARGE': 5000,
    'MEMORY_THRESHOLD_MB': 100,  # Threshold for chunked processing
    'ENABLE_MONITORING': True,
    'LOG_PERFORMANCE': True
}

def get_performance_recommendations(total_records):
    """Get performance recommendations for dataset size"""
    recommendations = []
    
    if total_records > 50000:
        recommendations.extend([
            "Use chunked processing for datasets over 50,000 records",
            "Consider streaming data from source instead of loading all at once",
            "Monitor memory usage during processing",
            "Use CSV intermediate files for very large datasets"
        ])
    elif total_records > 10000:
        recommendations.extend([
            "Consider chunked processing for better performance",
            "Monitor memory usage",
            "Use appropriate chunk sizes (1000-2000 records per chunk)"
        ])
    else:
        recommendations.append("Dataset size is manageable for direct processing")
    
    return recommendations
