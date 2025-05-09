#!/usr/bin/env python3
import re
import os
import statistics

def parse_ping_file(filename):
    try:
        with open(filename, 'r') as f:
            content = f.read()
        match = re.search(r'rtt min/avg/max/mdev = [\d.]+/([\d.]+)/[\d.]+/([\d.]+) ms', content)
        if match:
            avg_rtt = float(match.group(1))
            std_rtt = float(match.group(2))
            return avg_rtt, std_rtt
    except (IOError, AttributeError) as e:
        print(f"Error parsing {filename}: {e}")
        return None, None

def parse_iperf3_file(filename):
    try:
        with open(filename, 'r') as f:
            content = f.read()
        # Debug: Print full content of the file
        print(f"Content of {filename}:\n{content}\n---")
        
        # Extract raw Bandwidth values for each interval
        bandwidth_values = []
        interval_pattern = r'\[\s*\d+\]\s*[\d.-]+\s*sec\s*[\d.]+\s*\w+\s*([\d.]+)\s*([GM])bits/sec'
        for line in content.splitlines():
            match = re.search(interval_pattern, line)
            if match:
                bandwidth = float(match.group(1))
                unit = match.group(2)
                if unit == 'G':
                    bandwidth *= 1000  # Convert Gbits/sec to Mbits/sec
                bandwidth_values.append(bandwidth)
        
        if bandwidth_values:
            avg_throughput = statistics.mean(bandwidth_values)
            std_throughput = statistics.stdev(bandwidth_values) if len(bandwidth_values) > 1 else 0.0
            return avg_throughput, std_throughput, bandwidth_values
        else:
            print(f"No valid throughput data found in {filename}")
            return None, None, []
    except (IOError, AttributeError) as e:
        print(f"Error parsing {filename}: {e}")
        return None, None, []

def main():
    topologies = ['linear', 'minimal', 'tree', 'torus', 'full']
    results = {
        'Topology': [],
        'Avg RTT (ms)': [],
        'RTT Std Dev (ms)': [],
        'TCP Throughput (Mbps)': [],
        'TCP Std Dev (Mbps)': [],
        'UDP Throughput (Mbps)': [],
        'UDP Std Dev (Mbps)': [],
        'TCP Raw Bandwidth': [],
        'UDP Raw Bandwidth': []
    }
    
    for topo in topologies:
        avg_rtt, std_rtt = parse_ping_file(f'outputs/{topo}_ping_rtt.txt')
        tcp_avg, tcp_std, tcp_raw = parse_iperf3_file(f'outputs/{topo}_iperf3_tcp.txt')
        udp_avg, udp_std, udp_raw = parse_iperf3_file(f'outputs/{topo}_iperf3_udp.txt')
        
        results['Topology'].append(topo.capitalize())
        results['Avg RTT (ms)'].append(avg_rtt if avg_rtt is not None else 'N/A')
        results['RTT Std Dev (ms)'].append(std_rtt if std_rtt is not None else 'N/A')
        results['TCP Throughput (Mbps)'].append(tcp_avg if tcp_avg is not None else 'N/A')
        results['TCP Std Dev (Mbps)'].append(tcp_std if tcp_std is not None else 'N/A')
        results['UDP Throughput (Mbps)'].append(udp_avg if udp_avg is not None else 'N/A')
        results['UDP Std Dev (Mbps)'].append(udp_std if udp_std is not None else 'N/A')
        results['TCP Raw Bandwidth'].append(tcp_raw)
        results['UDP Raw Bandwidth'].append(udp_raw)
    
    print("\nResults Table:")
    print("%-10s %-15s %-20s %-25s %-25s %-25s %-25s" % (
        'Topology', 'Avg RTT (ms)', 'RTT Std Dev (ms)', 'TCP Throughput (Mbps)', 'TCP Std Dev (Mbps)', 
        'UDP Throughput (Mbps)', 'UDP Std Dev (Mbps)'
    ))
    print('-' * 130)
    for i in range(len(topologies)):
        print("%-10s %-15s %-20s %-25s %-25s %-25s %-25s" % (
            results['Topology'][i],
            results['Avg RTT (ms)'][i],
            results['RTT Std Dev (ms)'][i],
            results['TCP Throughput (Mbps)'][i],
            results['TCP Std Dev (Mbps)'][i],
            results['UDP Throughput (Mbps)'][i],
            results['UDP Std Dev (Mbps)'][i]
        ))
    
    with open('outputs/results_summary.txt', 'w') as f:
        f.write("Topology,Avg RTT (ms),RTT Std Dev (ms),TCP Throughput (Mbps),TCP Std Dev (Mbps),UDP Throughput (Mbps),UDP Std Dev (Mbps)\n")
        for i in range(len(topologies)):
            f.write("%s,%s,%s,%s,%s,%s,%s\n" % (
                results['Topology'][i],
                results['Avg RTT (ms)'][i],
                results['RTT Std Dev (ms)'][i],
                results['TCP Throughput (Mbps)'][i],
                results['TCP Std Dev (Mbps)'][i],
                results['UDP Throughput (Mbps)'][i],
                results['UDP Std Dev (Mbps)'][i]
            ))
    
    return results  # Return results for plotting

if __name__ == '__main__':
    main()
