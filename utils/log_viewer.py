"""
Log Viewer Utility for YBB API
Provides functions to read, filter, and display API logs
"""
import os
import json
from datetime import datetime, timedelta
import re

class YBBLogViewer:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.api_log_file = os.path.join(log_dir, "ybb_api.log")
        self.access_log_file = os.path.join(log_dir, "ybb_api_access.log")
    
    def read_recent_logs(self, log_type="all", lines=50):
        """
        Read recent log entries
        
        Args:
            log_type: "all", "api", "access"
            lines: Number of recent lines to read
        
        Returns:
            List of log entries
        """
        logs = []
        
        if log_type in ["all", "api"] and os.path.exists(self.api_log_file):
            logs.extend(self._read_file_tail(self.api_log_file, lines))
        
        if log_type in ["all", "access"] and os.path.exists(self.access_log_file):
            logs.extend(self._read_file_tail(self.access_log_file, lines))
        
        # Sort by timestamp
        logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return logs[:lines]
    
    def filter_logs(self, filters=None, hours=24):
        """
        Filter logs based on criteria
        
        Args:
            filters: Dict with filter criteria
                - request_id: Specific request ID
                - level: Log level (INFO, ERROR, WARNING)
                - endpoint: API endpoint pattern
                - ip: Client IP address
                - time_from: Start time (datetime)
                - time_to: End time (datetime)
            hours: Hours back to search (if time filters not provided)
        
        Returns:
            List of filtered log entries
        """
        if filters is None:
            filters = {}
        
        # Set time range if not provided
        if 'time_from' not in filters:
            filters['time_from'] = datetime.now() - timedelta(hours=hours)
        if 'time_to' not in filters:
            filters['time_to'] = datetime.now()
        
        all_logs = self.read_recent_logs("all", 1000)  # Read more logs for filtering
        filtered_logs = []
        
        for log_entry in all_logs:
            if self._matches_filters(log_entry, filters):
                filtered_logs.append(log_entry)
        
        return filtered_logs
    
    def get_request_timeline(self, request_id):
        """
        Get complete timeline for a specific request ID
        
        Args:
            request_id: Request ID to track
        
        Returns:
            List of log entries for the request
        """
        return self.filter_logs({'request_id': request_id})
    
    def get_error_summary(self, hours=24):
        """
        Get summary of errors in the specified time period
        
        Args:
            hours: Hours back to analyze
        
        Returns:
            Dict with error statistics
        """
        error_logs = self.filter_logs({'level': 'ERROR'}, hours)
        
        error_summary = {
            'total_errors': len(error_logs),
            'by_endpoint': {},
            'by_error_type': {},
            'recent_errors': error_logs[:10]
        }
        
        for log_entry in error_logs:
            # Count by endpoint
            endpoint = log_entry.get('endpoint', 'unknown')
            error_summary['by_endpoint'][endpoint] = error_summary['by_endpoint'].get(endpoint, 0) + 1
            
            # Count by error type
            message = log_entry.get('message', '')
            error_type = self._extract_error_type(message)
            error_summary['by_error_type'][error_type] = error_summary['by_error_type'].get(error_type, 0) + 1
        
        return error_summary
    
    def get_performance_summary(self, hours=24):
        """
        Get performance statistics
        
        Args:
            hours: Hours back to analyze
        
        Returns:
            Dict with performance statistics
        """
        access_logs = self.filter_logs({'log_type': 'access'}, hours)
        
        response_times = []
        request_counts = {'total': 0, 'by_endpoint': {}, 'by_method': {}}
        status_codes = {}
        
        for log_entry in access_logs:
            request_counts['total'] += 1
            
            # Extract response time
            message = log_entry.get('message', '')
            time_match = re.search(r'Time: ([\d.]+)ms', message)
            if time_match:
                response_times.append(float(time_match.group(1)))
            
            # Count by endpoint
            endpoint_match = re.search(r'URL: .*/api/([^?\s]+)', message)
            if endpoint_match:
                endpoint = endpoint_match.group(1)
                request_counts['by_endpoint'][endpoint] = request_counts['by_endpoint'].get(endpoint, 0) + 1
            
            # Count by method
            method_match = re.search(r'Method: (\w+)', message)
            if method_match:
                method = method_match.group(1)
                request_counts['by_method'][method] = request_counts['by_method'].get(method, 0) + 1
            
            # Count status codes
            status_match = re.search(r'Status: (\d+)', message)
            if status_match:
                status = status_match.group(1)
                status_codes[status] = status_codes.get(status, 0) + 1
        
        # Calculate statistics
        perf_summary = {
            'total_requests': request_counts['total'],
            'request_breakdown': request_counts,
            'status_codes': status_codes,
            'response_times': {
                'count': len(response_times),
                'avg': round(sum(response_times) / len(response_times), 2) if response_times else 0,
                'min': min(response_times) if response_times else 0,
                'max': max(response_times) if response_times else 0
            }
        }
        
        # Add percentiles
        if response_times:
            sorted_times = sorted(response_times)
            perf_summary['response_times']['p50'] = self._percentile(sorted_times, 50)
            perf_summary['response_times']['p95'] = self._percentile(sorted_times, 95)
            perf_summary['response_times']['p99'] = self._percentile(sorted_times, 99)
        
        return perf_summary
    
    def export_logs_to_file(self, filters=None, output_file="exported_logs.json"):
        """
        Export filtered logs to a file
        
        Args:
            filters: Filter criteria
            output_file: Output file path
        """
        logs = self.filter_logs(filters) if filters else self.read_recent_logs("all", 500)
        
        export_data = {
            'export_time': datetime.now().isoformat(),
            'total_entries': len(logs),
            'filters_applied': filters or {},
            'logs': logs
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return f"Exported {len(logs)} log entries to {output_file}"
    
    def _read_file_tail(self, file_path, lines):
        """Read last N lines from a file"""
        if not os.path.exists(file_path):
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_lines = f.readlines()
                recent_lines = file_lines[-lines:] if len(file_lines) > lines else file_lines
                
                parsed_logs = []
                for line in recent_lines:
                    log_entry = self._parse_log_line(line.strip())
                    if log_entry:
                        parsed_logs.append(log_entry)
                
                return parsed_logs
        except Exception as e:
            print(f"Error reading log file {file_path}: {e}")
            return []
    
    def _parse_log_line(self, line):
        """Parse a single log line into structured data"""
        try:
            # Pattern: TIMESTAMP | LEVEL | LOGGER | FUNCTION | MESSAGE
            pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| (\w+)\s*\| (.+?) \| (.+?) \| (.+)'
            match = re.match(pattern, line)
            
            if match:
                timestamp, level, logger, function, message = match.groups()
                
                # Extract additional info from message
                request_id = self._extract_request_id(message)
                endpoint = self._extract_endpoint(message)
                
                return {
                    'timestamp': timestamp,
                    'level': level.strip(),
                    'logger': logger.strip(),
                    'function': function.strip(),
                    'message': message.strip(),
                    'request_id': request_id,
                    'endpoint': endpoint,
                    'raw_line': line
                }
            else:
                # Simple format fallback
                if '|' in line:
                    parts = line.split('|', 2)
                    if len(parts) >= 3:
                        return {
                            'timestamp': parts[0].strip(),
                            'level': parts[1].strip(),
                            'message': parts[2].strip(),
                            'raw_line': line
                        }
        except Exception as e:
            pass
        
        return {'message': line, 'raw_line': line}
    
    def _extract_request_id(self, message):
        """Extract request ID from log message"""
        match = re.search(r'ID: ([a-f0-9]{8})', message)
        return match.group(1) if match else None
    
    def _extract_endpoint(self, message):
        """Extract endpoint from log message"""
        match = re.search(r'URL: .*/api/([^?\s]+)', message)
        if match:
            return match.group(1)
        
        # Try alternative patterns
        endpoint_patterns = [
            r'PARTICIPANTS_EXPORT',
            r'PAYMENTS_EXPORT',
            r'AMBASSADORS_EXPORT',
            r'DOWNLOAD',
            r'HEALTH_CHECK'
        ]
        
        for pattern in endpoint_patterns:
            if re.search(pattern, message):
                return pattern.lower().replace('_', '/')
        
        return None
    
    def _extract_error_type(self, message):
        """Extract error type from error message"""
        if 'timeout' in message.lower():
            return 'timeout'
        elif 'not found' in message.lower():
            return 'not_found'
        elif 'permission' in message.lower():
            return 'permission'
        elif 'validation' in message.lower():
            return 'validation'
        elif 'export failed' in message.lower():
            return 'export_failed'
        else:
            return 'unknown'
    
    def _matches_filters(self, log_entry, filters):
        """Check if log entry matches filter criteria"""
        # Time filter
        if 'time_from' in filters or 'time_to' in filters:
            try:
                log_time = datetime.strptime(log_entry.get('timestamp', ''), '%Y-%m-%d %H:%M:%S')
                if 'time_from' in filters and log_time < filters['time_from']:
                    return False
                if 'time_to' in filters and log_time > filters['time_to']:
                    return False
            except:
                pass
        
        # Request ID filter
        if 'request_id' in filters:
            if log_entry.get('request_id') != filters['request_id']:
                return False
        
        # Level filter
        if 'level' in filters:
            if log_entry.get('level') != filters['level']:
                return False
        
        # Endpoint filter
        if 'endpoint' in filters:
            endpoint_pattern = filters['endpoint']
            log_endpoint = log_entry.get('endpoint', '')
            if not re.search(endpoint_pattern, log_endpoint):
                return False
        
        # IP filter
        if 'ip' in filters:
            message = log_entry.get('message', '')
            if filters['ip'] not in message:
                return False
        
        return True
    
    def _percentile(self, data, percentile):
        """Calculate percentile of data"""
        if not data:
            return 0
        k = (len(data) - 1) * percentile / 100
        f = int(k)
        c = k - f
        if f == len(data) - 1:
            return data[f]
        return data[f] * (1 - c) + data[f + 1] * c


def main():
    """CLI interface for log viewer"""
    import argparse
    
    parser = argparse.ArgumentParser(description="YBB API Log Viewer")
    parser.add_argument('--type', choices=['all', 'api', 'access'], default='all', help='Log type to view')
    parser.add_argument('--lines', type=int, default=50, help='Number of recent lines to show')
    parser.add_argument('--request-id', help='Filter by specific request ID')
    parser.add_argument('--level', choices=['INFO', 'ERROR', 'WARNING'], help='Filter by log level')
    parser.add_argument('--hours', type=int, default=24, help='Hours back to search')
    parser.add_argument('--errors', action='store_true', help='Show error summary')
    parser.add_argument('--performance', action='store_true', help='Show performance summary')
    parser.add_argument('--export', help='Export logs to file')
    
    args = parser.parse_args()
    
    viewer = YBBLogViewer()
    
    if args.errors:
        summary = viewer.get_error_summary(args.hours)
        print(json.dumps(summary, indent=2, default=str))
    elif args.performance:
        summary = viewer.get_performance_summary(args.hours)
        print(json.dumps(summary, indent=2, default=str))
    elif args.request_id:
        logs = viewer.get_request_timeline(args.request_id)
        for log in logs:
            print(f"{log.get('timestamp', 'N/A')} | {log.get('level', 'N/A')} | {log.get('message', 'N/A')}")
    else:
        filters = {}
        if args.level:
            filters['level'] = args.level
        
        logs = viewer.filter_logs(filters, args.hours) if filters else viewer.read_recent_logs(args.type, args.lines)
        
        for log in logs:
            print(f"{log.get('timestamp', 'N/A')} | {log.get('level', 'N/A')} | {log.get('message', 'N/A')}")
    
    if args.export:
        filters = {}
        if args.level:
            filters['level'] = args.level
        if args.request_id:
            filters['request_id'] = args.request_id
        
        result = viewer.export_logs_to_file(filters, args.export)
        print(result)


if __name__ == "__main__":
    main()
