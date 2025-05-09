#!/usr/bin/env python

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.node import Controller
from mininet.log import setLogLevel
import argparse
import sys

class SingleSwitchTopo(Topo):
    def build(self, n=7):
        switch = self.addSwitch('s1')
        for i in range(1, n + 1):
            host = self.addHost('h%d' % i)
            self.addLink(host, switch)

def main():
    setLogLevel('info')

    parser = argparse.ArgumentParser(description='Basic Single Switch Topology')
    parser.add_argument('--hosts', type=int, default=7, help='Number of hosts to create')
    args = parser.parse_args()

    topo = SingleSwitchTopo(n=args.hosts)
    net = Mininet(topo=topo, controller=Controller)
    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    main()

