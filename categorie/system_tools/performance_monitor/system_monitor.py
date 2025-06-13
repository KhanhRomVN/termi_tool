import psutil
import os
from typing import Dict, List, Tuple
from datetime import datetime
import json

class SystemMonitor:
    @staticmethod
    def get_cpu_usage() -> Dict:
        """Get CPU usage information"""
        cpu_info = {
            'total_usage': psutil.cpu_percent(interval=1),
            'per_cpu': psutil.cpu_percent(interval=1, percpu=True),
            'cores': psutil.cpu_count(),
            'physical_cores': psutil.cpu_count(logical=False),
            'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
            'stats': psutil.cpu_stats()._asdict()
        }
        return cpu_info

    @staticmethod
    def get_ram_usage() -> Dict:
        """Get RAM usage information"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        ram_info = {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'free': memory.free,
            'percent': memory.percent,
            'swap': swap._asdict()
        }
        return ram_info

    @staticmethod
    def get_storage_info() -> List[Dict]:
        """Get storage information for all partitions"""
        partitions = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partition_info = {
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                }
                partitions.append(partition_info)
            except Exception:
                continue
        return partitions

    @staticmethod
    def get_process_list() -> List[Dict]:
        """Get list of running processes sorted by memory usage"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                pinfo = proc.info
                pinfo['memory_mb'] = proc.memory_info().rss / (1024 * 1024)  # Convert to MB
                processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Sort by memory usage
        return sorted(processes, key=lambda x: x.get('memory_mb', 0), reverse=True)

def format_bytes(bytes: int) -> str:
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} PB"

def main():
    """CLI interface for system monitoring"""
    import argparse
    
    parser = argparse.ArgumentParser(description="System Monitoring Tools")
    parser.add_argument("command", choices=['cpu', 'ram', 'storage', 'processes'],
                      help="Command to execute")
    parser.add_argument("--json", action="store_true",
                      help="Output in JSON format")
    
    args = parser.parse_args()
    
    if args.command == "cpu":
        info = SystemMonitor.get_cpu_usage()
        if args.json:
            print(json.dumps(info, indent=2))
        else:
            print("\nCPU Information:")
            print(f"Total CPU Usage: {info['total_usage']}%")
            print(f"Per CPU Usage: {info['per_cpu']}")
            print(f"Total Cores: {info['cores']}")
            print(f"Physical Cores: {info['physical_cores']}")
            if info['freq']:
                print(f"CPU Frequency: {info['freq']['current']:.2f} MHz")
    
    elif args.command == "ram":
        info = SystemMonitor.get_ram_usage()
        if args.json:
            print(json.dumps(info, indent=2))
        else:
            print("\nRAM Information:")
            print(f"Total RAM: {format_bytes(info['total'])}")
            print(f"Used RAM: {format_bytes(info['used'])} ({info['percent']}%)")
            print(f"Available RAM: {format_bytes(info['available'])}")
            print(f"Free RAM: {format_bytes(info['free'])}")
            print("\nSwap Information:")
            print(f"Total Swap: {format_bytes(info['swap']['total'])}")
            print(f"Used Swap: {format_bytes(info['swap']['used'])} ({info['swap']['percent']}%)")
    
    elif args.command == "storage":
        info = SystemMonitor.get_storage_info()
        if args.json:
            print(json.dumps(info, indent=2))
        else:
            print("\nStorage Information:")
            for partition in info:
                print(f"\nDevice: {partition['device']}")
                print(f"Mount Point: {partition['mountpoint']}")
                print(f"File System: {partition['fstype']}")
                print(f"Total Space: {format_bytes(partition['total'])}")
                print(f"Used Space: {format_bytes(partition['used'])} ({partition['percent']}%)")
                print(f"Free Space: {format_bytes(partition['free'])}")
    
    elif args.command == "processes":
        info = SystemMonitor.get_process_list()
        if args.json:
            print(json.dumps(info, indent=2))
        else:
            print("\nTop Processes by Memory Usage:")
            print(f"{'PID':>7} {'Memory (MB)':>12} {'CPU %':>7} {'Status':>10} Process Name")
            print("-" * 60)
            for proc in info[:20]:  # Show top 20 processes
                print(f"{proc['pid']:>7} {proc['memory_mb']:>12.2f} {proc['cpu_percent']:>7.1f} "
                      f"{proc['status']:>10} {proc['name']}")

if __name__ == "__main__":
    main() 