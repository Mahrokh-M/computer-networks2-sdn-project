#!/usr/bin/env python
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.node import OVSController, OVSSwitch
from mininet.log import setLogLevel
import time
import subprocess

class TorusTopo(Topo):
    def build(self):
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        h1 = self.addHost('h1', ip='10.0.0.1/24')
        h2 = self.addHost('h2', ip='10.0.0.2/24')
        h3 = self.addHost('h3', ip='10.0.0.3/24')
        h4 = self.addHost('h4', ip='10.0.0.4/24')
        self.addLink(s1, s2)
        self.addLink(s2, s3)
        self.addLink(s3, s4)
        self.addLink(s4, s1)
        self.addLink(s1, h1)
        self.addLink(s2, h2)
        self.addLink(s3, h3)
        self.addLink(s4, h4)

def run_tests(net, topo_name):
    # Ensure all interfaces are up
    for host in net.hosts:
        host.cmd('ifconfig {}-eth0 up'.format(host.name))
    
    # Clean up any existing iperf3 processes
    for host in net.hosts:
        host.cmd('killall iperf3 || true')
    
    # Enable STP on all switches
    for switch in net.switches:
        switch.cmd('ovs-vsctl set bridge %s stp_enable=true' % switch.name)
    
    # Wait longer for STP to stabilize
    time.sleep(30)
    
    # Run pingall test
    result = net.pingAll()
    with open('outputs/%s_pingall.txt' % topo_name, 'w') as f:
        f.write('Pingall Result: %s%%\n' % result)
    
    # Run ping test
    h1 = net.get('h1')
    ping_output = h1.cmd('ping -c 10 10.0.0.3')
    with open('outputs/%s_ping_rtt.txt' % topo_name, 'w') as f:
        f.write(ping_output)
    
    h3 = net.get('h3')
    h3.cmd('killall iperf3 || true')
    time.sleep(1)
    
    # Run iperf3 TCP test
    iperf_server = h3.popen('iperf3 -s -p 5001')
    time.sleep(2)
    iperf_tcp_output = h1.cmd('iperf3 -c 10.0.0.3 -p 5001 -t 10')
    with open('outputs/%s_iperf3_tcp.txt' % topo_name, 'w') as f:
        f.write(iperf_tcp_output)
    iperf_server.terminate()
    h3.cmd('killall iperf3 || true')
    time.sleep(1)
    
    # Run iperf3 UDP test
    iperf_server = h3.popen('iperf3 -s -p 5001')
    time.sleep(2)
    iperf_udp_output = h1.cmd('iperf3 -c 10.0.0.3 -u -p 5001 -t 10 -b 100M')
    with open('outputs/%s_iperf3_udp.txt' % topo_name, 'w') as f:
        f.write(iperf_udp_output)
    iperf_server.terminate()
    h3.cmd('killall iperf3 || true')

def main():
    setLogLevel('info')
    topo = TorusTopo()
    net = Mininet(topo=topo, controller=OVSController, switch=OVSSwitch)
    net.start()
    run_tests(net, 'torus')
    CLI(net)
    net.stop()

if __name__ == '__main__':
    main()
