import pyshark
import argparse
from datetime import datetime
import json
from typing import Optional, Dict, List
import os

class RequestLogger:
    def __init__(self, interface: str, output_file: Optional[str] = None):
        self.interface = interface
        self.output_file = output_file
        self.captured_packets = []

    def start_capture(self, duration: Optional[int] = None, packet_count: Optional[int] = None):
        """Start capturing network packets"""
        # Create capture object
        capture = pyshark.LiveCapture(interface=self.interface)

        print(f"\nStarting capture on interface {self.interface}...")
        print("Press Ctrl+C to stop capturing\n")

        try:
            # Set up capture parameters
            if packet_count:
                packets = capture.sniff_continuously(packet_count=packet_count)
            elif duration:
                packets = capture.sniff_continuously(timeout=duration)
            else:
                packets = capture.sniff_continuously()

            # Process packets
            for packet in packets:
                if hasattr(packet, 'http') or hasattr(packet, 'https'):
                    self._process_http_packet(packet)
                elif hasattr(packet, 'dns'):
                    self._process_dns_packet(packet)
                elif hasattr(packet, 'tls'):
                    self._process_tls_packet(packet)

        except KeyboardInterrupt:
            print("\nCapture stopped by user")
        finally:
            capture.close()
            self._save_results()

    def _process_http_packet(self, packet):
        """Process HTTP/HTTPS packet"""
        try:
            if hasattr(packet, 'http'):
                layer = packet.http
                protocol = 'HTTP'
            else:
                layer = packet.https
                protocol = 'HTTPS'

            packet_info = {
                'timestamp': packet.sniff_time.isoformat(),
                'protocol': protocol,
                'src_ip': packet.ip.src if hasattr(packet, 'ip') else None,
                'dst_ip': packet.ip.dst if hasattr(packet, 'ip') else None,
                'method': layer.request_method if hasattr(layer, 'request_method') else None,
                'host': layer.host if hasattr(layer, 'host') else None,
                'uri': layer.request_uri if hasattr(layer, 'request_uri') else None,
                'user_agent': layer.user_agent if hasattr(layer, 'user_agent') else None,
                'status_code': layer.response_code if hasattr(layer, 'response_code') else None
            }
            self.captured_packets.append(packet_info)
            self._print_packet_info(packet_info)

        except Exception as e:
            print(f"Error processing HTTP packet: {e}")

    def _process_dns_packet(self, packet):
        """Process DNS packet"""
        try:
            packet_info = {
                'timestamp': packet.sniff_time.isoformat(),
                'protocol': 'DNS',
                'src_ip': packet.ip.src if hasattr(packet, 'ip') else None,
                'dst_ip': packet.ip.dst if hasattr(packet, 'ip') else None,
                'query': packet.dns.qry_name if hasattr(packet.dns, 'qry_name') else None,
                'response': packet.dns.resp_name if hasattr(packet.dns, 'resp_name') else None
            }
            self.captured_packets.append(packet_info)
            self._print_packet_info(packet_info)

        except Exception as e:
            print(f"Error processing DNS packet: {e}")

    def _process_tls_packet(self, packet):
        """Process TLS packet"""
        try:
            packet_info = {
                'timestamp': packet.sniff_time.isoformat(),
                'protocol': 'TLS',
                'src_ip': packet.ip.src if hasattr(packet, 'ip') else None,
                'dst_ip': packet.ip.dst if hasattr(packet, 'ip') else None,
                'handshake_type': packet.tls.handshake_type if hasattr(packet.tls, 'handshake_type') else None,
                'server_name': packet.tls.handshake_extensions_server_name if hasattr(packet.tls, 'handshake_extensions_server_name') else None
            }
            self.captured_packets.append(packet_info)
            self._print_packet_info(packet_info)

        except Exception as e:
            print(f"Error processing TLS packet: {e}")

    def _print_packet_info(self, packet_info: Dict):
        """Print packet information in a readable format"""
        print("\n--- New Packet ---")
        for key, value in packet_info.items():
            if value is not None:
                print(f"{key.replace('_', ' ').title()}: {value}")

    def _save_results(self):
        """Save captured packets to file if output file is specified"""
        if self.output_file and self.captured_packets:
            try:
                with open(self.output_file, 'w') as f:
                    json.dump(self.captured_packets, f, indent=2)
                print(f"\nResults saved to {self.output_file}")
            except Exception as e:
                print(f"Error saving results: {e}")

def list_interfaces() -> List[str]:
    """List available network interfaces"""
    try:
        import netifaces
        return netifaces.interfaces()
    except ImportError:
        print("netifaces package not installed. Unable to list interfaces.")
        return []

def main():
    parser = argparse.ArgumentParser(description="Network Request Logger")
    parser.add_argument("--interface", "-i", help="Network interface to capture")
    parser.add_argument("--output", "-o", help="Output file for captured packets")
    parser.add_argument("--duration", "-d", type=int, help="Capture duration in seconds")
    parser.add_argument("--count", "-c", type=int, help="Number of packets to capture")
    parser.add_argument("--list-interfaces", "-l", action="store_true",
                      help="List available network interfaces")

    args = parser.parse_args()

    if args.list_interfaces:
        interfaces = list_interfaces()
        if interfaces:
            print("\nAvailable network interfaces:")
            for interface in interfaces:
                print(f"- {interface}")
        return

    if not args.interface:
        print("Error: Network interface is required")
        parser.print_help()
        return

    logger = RequestLogger(args.interface, args.output)
    logger.start_capture(args.duration, args.count)

if __name__ == "__main__":
    main() 