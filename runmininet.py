from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import CPULimitedHost
from mininet.link import TCLink
import sys

# Single switch topology


class SingleSwitchTopo(Topo):
    def __init__(self, n):
        # Initialize the base class
        Topo.__init__(self, n)
        # Add the switch to the topology
        switch = self.addSwitch('s1')
        # Add 'n' hosts to the topology
        hosts = [self.addHost(f'h{i+1}', cpu=.5/n) for i in range(n)]
        # Add links between the switch and each host
        for j in range(n):
            self.addLink(hosts[j], switch, bw=10, delay='5ms',
                         loss=10, max_queue_size=1000)

# Linear topology


class LinearTopo(Topo):
    def __init__(self, n):
        Topo.__init__(self)
        switches = [self.addSwitch(f's{i+1}') for i in range(n)]
        hosts = [self.addHost(f'h{j+1}', cpu=.5/n) for j in range(n)]
        # Add links between hosts and their corresponding switches
        for i in range(n):
            self.addLink(hosts[i], switches[i], bw=10,
                         delay='5ms', loss=10, max_queue_size=1000)
            # If this is not the last host, add a link to the next switch
            if i < n-1:
                self.addLink(switches[i], switches[i+1], bw=10,
                             delay='5ms', loss=10, max_queue_size=1000)

# Tree topology


class TreeTopo(Topo):
    def __init__(self, depth):
        Topo.__init__(self, depth)
        a, b, s_count, h_count, snh = 1, 2, 2, 1, [self.addSwitch('s1')]
        # Construct the tree and add links
        for i in range((2**(depth+1)-1)//2):
            # If this node is a leaf, add two hosts to the topology
            if i >= ((2**depth)//2)-1:
                snh.append(self.addHost(f'h{h_count}', cpu=.5/depth))
                snh.append(self.addHost(f'h{h_count+1}', cpu=.5/depth))
                h_count += 2
            # Otherwise, add two switches to the topology
            else:
                snh.append(self.addSwitch(f's{s_count}'))
                snh.append(self.addSwitch(f's{s_count+1}'))
                s_count += 2
            # Add links between the current node and its children
            self.addLink(snh[i], snh[a+i], bw=10, delay='5ms',
                         loss=10, max_queue_size=1000)
            self.addLink(snh[i], snh[b+i], bw=10, delay='5ms',
                         loss=10, max_queue_size=1000)
            # Update 'a' and 'b' to point
            a, b = b, b+1

# Mesh topology


class MeshTopo(Topo):
    def __init__(self, n):
        Topo.__init__(self, n)
        switches = [self.addSwitch(f's{i+1}') for i in range(n)]
        hosts = [self.addHost(f'h{j+1}', cpu=.5/n) for j in range(n)]

        # Add links between switches
        for i in range(n):
            for j in range(i+1, n):
                self.addLink(switches[i], switches[j], bw=10,
                             delay='5ms', loss=10, max_queue_size=1000)

        # Add links between hosts and switches
        for i in range(n):
            self.addLink(hosts[i], switches[i], bw=10,
                         delay='5ms', loss=10, max_queue_size=1000)

# Performance test


def perfTest():

    # Check command line arguments to determine which topology to use
    if sys.argv[1] == "single":
        topo = SingleSwitchTopo(int(sys.argv[2]))
    elif sys.argv[1] == "linear":
        topo = LinearTopo(int(sys.argv[2]))
    elif sys.argv[1] == "tree":
        topo = TreeTopo(int(sys.argv[2]))
    elif sys.argv[1] == "mesh":
        topo = MeshTopo(int(sys.argv[2]))
    else:
        print("unknown topology")

    # Create network with specified topology, using CPULimitedHost and TCLink
    net = Mininet(topo, host=CPULimitedHost, link=TCLink)
    net.start()

    # Print information about host connections in network
    print("\n dumping host connections: \n")
    dumpNodeConnections(net.hosts)

    # Test network connectivity using pingAll()
    print("\n Testing network connectivity: \n")
    net.pingAll()

    # Test pairwise bandwidths between hosts using iperf()
    print("\n Testing all pairwise bandwidths between hosts: \n")
    for i in range(len(net.hosts)):
        for j in range(i+1, len(net.hosts)):
            net.iperf((net.get(f'h{i+1}'), net.get(f'h{j+1}')))

    # Stop the network
    print("\n Stopping Network \n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    perfTest()
