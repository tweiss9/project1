from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
import sys

class MyTopo(Topo):
    def __init__(self, n):
        Topo.__init__(self)
        # Add hosts
        for i in range(n):
            host = self.addHost('h{}'.format(i+1), cpu=.5/n)
        # Add switches
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        # Add links between hosts and switches
        for i in range(n):
            self.addLink('h{}'.format(i+1), switch1, bw=10, delay='5ms', loss=10, max_queue_size=1000)
            self.addLink('h{}'.format(i+1), switch2, bw=10, delay='5ms', loss=10, max_queue_size=1000)
        # Add link between switches
        self.addLink(switch1, switch2, bw=10, delay='5ms', loss=10, max_queue_size=1000)

if __name__ == '__main__':
    # Get topology and n from command line arguments
    topo = sys.argv[1]
    n = int(sys.argv[2])
    # Create topology object based on input
    if topo == 'linear':
        topology = MyTopo(n)
    elif topo == 'ring':
        topology = MyTopo(n)
        # Add link between last host and first host to create a ring topology
        topology.addLink('h1', 'h{}'.format(n), bw=10, delay='5ms', loss=10, max_queue_size=1000)
    else:
        print('Unknown topology')
        sys.exit(1)
    # Create Mininet network object
    net = Mininet(topo=topology, host=CPULimitedHost, link=TCLink)
    # Start network
    net.start()
    # Open Mininet CLI
    net.interact()
    # Stop network
    net.stop()