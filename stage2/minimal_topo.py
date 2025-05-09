#!/usr/bin/env python
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.node import Controller
from mininet.log import setLogLevel
import time
import os
import subprocess

class MinimalTopo(Topo):
    def build(self):
        switch = self.addSwitch('s1')
        h1 = self.addHost('h1', ip='10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.0.2')
        self.addLink(h1, switch)
        self.addLink(h2, switch)

def run_tests(net, topo_name):
    result = net.pingAll()
    with open('outputs/%s_pingall.txt' % topo_name, 'w') as f:
        f.write('Pingall Result: %s%%\n' % result)
    
    h1 = net.get('h1')
    ping_output = h1.cmd('ping -c 10 10.0.0.2')
    with open('outputs/%s_ping_rtt.txt' % topo_name, 'w') as f:
        f.write(ping_output)
    
    h2 = net.get('h2')
    h2.cmd('killall iperf3 || true')
    time.sleep(1)
    
    iperf_server = h2.popen('iperf3 -s -p 5001')
    time.sleep(2)
    iperf_tcp_output = h1.cmd('iperf3 -c 10.0.0.2 -p 5001 -t 10')
    with open('outputs/%s_iperf3_tcp.txt' % topo_name, 'w') as f:
        f.write(iperf_tcp_output)
    iperf_server.terminate()
    h2.cmd('killall iperf3 || true')
    time.sleep(1)
    
    iperf_server = h2.popen('iperf3 -s -p 5001')
    time.sleep(2)
    iperf_udp_output = h1.cmd('iperf3 -c 10.0.0.2 -u -p 5001 -t 10 -b 100M')
    with open('outputs/%s_iperf3_udp.txt' % topo_name, 'w') as f:
        f.write(iperf_udp_output)
    iperf_server.terminate()
    h2.cmd('killall iperf3 || true')

def main():
    setLogLevel('info')
    topo = MinimalTopo()
    net = Mininet(topo=topo, controller=Controller)
    net.start()
    run_tests(net, 'minimal')
    CLI(net)
    net.stop()

if __name__ == '__main__':
    main()
