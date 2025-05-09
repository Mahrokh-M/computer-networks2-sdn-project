#!/usr/bin/env python
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.node import Controller
from mininet.log import setLogLevel
import time
import os
import subprocess

class TreeTopo(Topo):
    def build(self):
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        h1 = self.addHost('h1', ip='10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.0.2')
        h3 = self.addHost('h3', ip='10.0.0.3')
        h4 = self.addHost('h4', ip='10.0.0.4')
        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s2, s4)
        self.addLink(s2, h1)
        self.addLink(s3, h2)
        self.addLink(s4, h3)
        self.addLink(s4, h4)

def run_tests(net, topo_name):
    result = net.pingAll()
    with open('outputs/%s_pingall.txt' % topo_name, 'w') as f:
        f.write('Pingall Result: %s%%\n' % result)
    
    h1 = net.get('h1')
    ping_output = h1.cmd('ping -c 10 10.0.0.4')
    with open('outputs/%s_ping_rtt.txt' % topo_name, 'w') as f:
        f.write(ping_output)
    
    h4 = net.get('h4')
    h4.cmd('killall iperf3 || true')
    time.sleep(1)
    
    iperf_server = h4.popen('iperf3 -s -p 5001')
    time.sleep(2)
    iperf_tcp_output = h1.cmd('iperf3 -c 10.0.0.4 -p 5001 -t 10')
    with open('outputs/%s_iperf3_tcp.txt' % topo_name, 'w') as f:
        f.write(iperf_tcp_output)
    iperf_server.terminate()
    h4.cmd('killall iperf3 || true')
    time.sleep(1)
    
    iperf_server = h4.popen('iperf3 -s -p 5001')
    time.sleep(2)
    iperf_udp_output = h1.cmd('iperf3 -c 10.0.0.4 -u -p 5001 -t 10 -b 100M')
    with open('outputs/%s_iperf3_udp.txt' % topo_name, 'w') as f:
        f.write(iperf_udp_output)
    iperf_server.terminate()
    h4.cmd('killall iperf3 || true')

def main():
    setLogLevel('info')
    topo = TreeTopo()
    net = Mininet(topo=topo, controller=Controller)
    net.start()
    run_tests(net, 'tree')
    CLI(net)
    net.stop()

if __name__ == '__main__':
    main()
