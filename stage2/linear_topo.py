#!/usr/bin/env python
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.node import Controller
from mininet.log import setLogLevel
import time
import os
import subprocess

class LinearTopo(Topo):
    def build(self, n=4):
        switches = []
        for i in range(1, n+1):
            switch = self.addSwitch('s%d' % i)
            switches.append(switch)
            host = self.addHost('h%d' % i, ip='10.0.0.%d' % i)
            self.addLink(host, switch)
        for i in range(n-1):
            self.addLink(switches[i], switches[i+1])

def run_tests(net, topo_name):
    # Run pingall test
    result = net.pingAll()
    with open('outputs/%s_pingall.txt' % topo_name, 'w') as f:
        f.write('Pingall Result: %s%%\n' % result)
    
    # Run ping test
    h1 = net.get('h1')
    ping_output = h1.cmd('ping -c 10 10.0.0.4')
    with open('outputs/%s_ping_rtt.txt' % topo_name, 'w') as f:
        f.write(ping_output)
    
    # Ensure no existing iperf3 processes
    h4 = net.get('h4')
    h4.cmd('killall iperf3 || true')
    time.sleep(1)
    
    # Run iperf3 TCP test
    iperf_server = h4.popen('iperf3 -s -p 5001')
    time.sleep(2)
    iperf_tcp_output = h1.cmd('iperf3 -c 10.0.0.4 -p 5001 -t 10')
    with open('outputs/%s_iperf3_tcp.txt' % topo_name, 'w') as f:
        f.write(iperf_tcp_output)
    iperf_server.terminate()
    h4.cmd('killall iperf3 || true')
    time.sleep(1)
    
    # Run iperf3 UDP test
    iperf_server = h4.popen('iperf3 -s -p 5001')  # No -u for server
    time.sleep(2)
    iperf_udp_output = h1.cmd('iperf3 -c 10.0.0.4 -u -p 5001 -t 10 -b 100M')
    with open('outputs/%s_iperf3_udp.txt' % topo_name, 'w') as f:
        f.write(iperf_udp_output)
    iperf_server.terminate()
    h4.cmd('killall iperf3 || true')

def main():
    setLogLevel('info')
    topo = LinearTopo(n=4)
    net = Mininet(topo=topo, controller=Controller)
    net.start()
    run_tests(net, 'linear')
    CLI(net)
    net.stop()

if __name__ == '__main__':
    main()
