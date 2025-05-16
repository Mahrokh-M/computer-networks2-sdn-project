from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def treeTopo():
    net = Mininet(controller=RemoteController, switch=OVSSwitch)

    # Add controller
    info("*** Adding controller\n")
    net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)

    # Add hosts
    info("*** Adding hosts\n")
    h1 = net.addHost('h1', ip='10.0.0.1', mac='00:00:00:00:00:01')
    h2 = net.addHost('h2', ip='10.0.0.2', mac='00:00:00:00:00:02')
    h3 = net.addHost('h3', ip='10.0.0.3', mac='00:00:00:00:00:03')
    h4 = net.addHost('h4', ip='10.0.0.4', mac='00:00:00:00:00:04')

    # Add switches
    info("*** Adding switches\n")
    s1 = net.addSwitch('s1', protocols='OpenFlow13')
    s2 = net.addSwitch('s2', protocols='OpenFlow13')
    s3 = net.addSwitch('s3', protocols='OpenFlow13')
    s4 = net.addSwitch('s4', protocols='OpenFlow13')

    # Add links
    info("*** Adding links\n")
    net.addLink(s1, s2)  # s1-eth1 to s2-eth1
    net.addLink(s1, s3)  # s1-eth2 to s3-eth1
    net.addLink(s2, s4)  # s2-eth3 to s4-eth1
    net.addLink(s2, h1)  # s2-eth2 to h1-eth0
    net.addLink(s3, h2)  # s3-eth2 to h2-eth0
    net.addLink(s4, h3)  # s4-eth2 to h3-eth0
    net.addLink(s4, h4)  # s4-eth3 to h4-eth0

    # Start network
    info("*** Starting network\n")
    net.start()

    # Configure switches for OpenFlow 1.3
    for switch in [s1, s2, s3, s4]:
        switch.cmd('ovs-vsctl set Bridge {} protocols=OpenFlow13'.format(switch.name))

    # Start CLI
    info("*** Running CLI\n")
    CLI(net)

    # Stop network
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    treeTopo()
