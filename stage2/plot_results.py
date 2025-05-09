#!/usr/bin/env python3
import matplotlib.pyplot as plt
import csv
import os
from parse_raw_rtt import parse_raw_rtt
from parse_results import parse_iperf3_file  # Import to get raw Throughput values

def read_results(filename):
    results = {
        'Topology': [],
        'Avg RTT (ms)': [],
        'RTT Std Dev (ms)': [],
        'TCP Throughput (Mbps)': [],
        'TCP Std Dev (Mbps)': [],
        'UDP Throughput (Mbps)': [],
        'UDP Std Dev (Mbps)': []
    }
    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                results['Topology'].append(row['Topology'])
                results['Avg RTT (ms)'].append(float(row['Avg RTT (ms)']) if row['Avg RTT (ms)'] != 'N/A' else None)
                results['RTT Std Dev (ms)'].append(float(row['RTT Std Dev (ms)']) if row['RTT Std Dev (ms)'] != 'N/A' else None)
                results['TCP Throughput (Mbps)'].append(float(row['TCP Throughput (Mbps)']) if row['TCP Throughput (Mbps)'] != 'N/A' else None)
                results['TCP Std Dev (Mbps)'].append(float(row['TCP Std Dev (Mbps)']) if row['TCP Std Dev (Mbps)'] != 'N/A' else None)
                results['UDP Throughput (Mbps)'].append(float(row['UDP Throughput (Mbps)']) if row['UDP Throughput (Mbps)'] != 'N/A' else None)
                results['UDP Std Dev (Mbps)'].append(float(row['UDP Std Dev (Mbps)']) if row['UDP Std Dev (Mbps)'] != 'N/A' else None)
        return results
    except (IOError, ValueError) as e:
        print(f"Error reading {filename}: {e}")
        return None

def plot_bar(data, x_key, y_key, title, ylabel, filename):
    plt.figure(figsize=(10, 6))
    valid_data = [(t, y) for t, y in zip(data[x_key], data[y_key]) if y is not None]
    if not valid_data:
        print(f"No valid data available for {y_key}. Skipping plot for {filename}.")
        return
    topologies, values = zip(*valid_data)
    plt.bar(topologies, values)
    plt.title(title)
    plt.xlabel('Topology')
    plt.ylabel(ylabel)
    plt.grid(True, axis='y')
    plt.savefig(filename)
    print(f"Bar chart saved as {filename}")
    plt.close()

def plot_box(data, topologies, title, ylabel, filename):
    plt.figure(figsize=(10, 6))
    valid_data = [values for values in data if values]
    if not valid_data:
        print(f"No valid data for box plot. Skipping {filename}.")
        return
    plt.boxplot(valid_data, labels=topologies)
    plt.title(title)
    plt.xlabel('Topology')
    plt.ylabel(ylabel)
    plt.grid(True, axis='y')
    plt.savefig(filename)
    print(f"Box plot saved as {filename}")
    plt.close()

def main():
    results_file = 'outputs/results_summary.txt'
    if not os.path.exists(results_file):
        print(f"Results file {results_file} not found")
        return
    
    # Read summary results for Bar Charts
    results = read_results(results_file)
    if results is None:
        return
    
    # Get raw RTT values for Box Plot
    topologies = ['linear', 'minimal', 'tree', 'torus', 'full']
    rtt_data = []
    tcp_data = []
    udp_data = []
    for topo in topologies:
        _, _, rtt_values = parse_raw_rtt(f'outputs/{topo}_ping_rtt.txt')
        _, _, tcp_values = parse_iperf3_file(f'outputs/{topo}_iperf3_tcp.txt')
        _, _, udp_values = parse_iperf3_file(f'outputs/{topo}_iperf3_udp.txt')
        rtt_data.append(rtt_values)
        tcp_data.append(tcp_values)
        udp_data.append(udp_values)
    
    # Plot Bar Charts
    plot_bar(
        results,
        'Topology',
        'Avg RTT (ms)',
        'Average RTT Across Topologies',
        'Avg RTT (ms)',
        'outputs/rtt_bar_plot.png'
    )
    plot_bar(
        results,
        'Topology',
        'TCP Throughput (Mbps)',
        'TCP Throughput Across Topologies',
        'Throughput (Mbps)',
        'outputs/tcp_throughput_bar_plot.png'
    )
    plot_bar(
        results,
        'Topology',
        'UDP Throughput (Mbps)',
        'UDP Throughput Across Topologies',
        'Throughput (Mbps)',
        'outputs/udp_throughput_bar_plot.png'
    )
    
    # Plot Box Plots
    plot_box(
        rtt_data,
        [topo.capitalize() for topo in topologies],
        'RTT Distribution Across Topologies',
        'RTT (ms)',
        'outputs/rtt_box_plot.png'
    )
    plot_box(
        tcp_data,
        [topo.capitalize() for topo in topologies],
        'TCP Throughput Distribution Across Topologies',
        'Throughput (Mbps)',
        'outputs/tcp_throughput_box_plot.png'
    )
    plot_box(
        udp_data,
        [topo.capitalize() for topo in topologies],
        'UDP Throughput Distribution Across Topologies',
        'Throughput (Mbps)',
        'outputs/udp_throughput_box_plot.png'
    )

if __name__ == '__main__':
    main()
