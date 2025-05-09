#!/usr/bin/env python3
import re
import os
import statistics

def parse_raw_rtt(filename):
    try:
        with open(filename, 'r') as f:
            content = f.read()
        # Extract RTT values from ping output (e.g., "time=0.123 ms")
        rtt_values = []
        for line in content.splitlines():
            match = re.search(r'time=([\d.]+)\s*ms', line)
            if match:
                rtt_values.append(float(match.group(1)))
        if rtt_values:
            avg_rtt = statistics.mean(rtt_values)
            std_rtt = statistics.stdev(rtt_values) if len(rtt_values) > 1 else 0.0
            return avg_rtt, std_rtt, rtt_values  # Return raw RTT values for Box Plot
        else:
            print(f"No RTT values found in {filename}")
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
        'Raw RTT Values': []
    }
    
    for topo in topologies:
        filename = f'outputs/{topo}_ping_rtt.txt'
        avg_rtt, std_rtt, rtt_values = parse_raw_rtt(filename)
        
        results['Topology'].append(topo.capitalize())
        results['Avg RTT (ms)'].append(avg_rtt if avg_rtt is not None else 'N/A')
        results['RTT Std Dev (ms)'].append(std_rtt if std_rtt is not None else 'N/A')
        results['Raw RTT Values'].append(rtt_values)
    
    print("\nRaw RTT Results:")
    print("%-10s %-15s %-20s" % ('Topology', 'Avg RTT (ms)', 'RTT Std Dev (ms)'))
    print('-' * 45)
    for i in range(len(topologies)):
        print("%-10s %-15s %-20s" % (
            results['Topology'][i],
            results['Avg RTT (ms)'][i],
            results['RTT Std Dev (ms)'][i]
        ))
    
    with open('outputs/raw_rtt_summary.txt', 'w') as f:
        f.write("Topology,Avg RTT (ms),RTT Std Dev (ms)\n")
        for i in range(len(topologies)):
            f.write("%s,%s,%s\n" % (
                results['Topology'][i],
                results['Avg RTT (ms)'][i],
                results['RTT Std Dev (ms)'][i]
            ))
    
    return results  # Return results for use in plotting

if __name__ == '__main__':
    main()
