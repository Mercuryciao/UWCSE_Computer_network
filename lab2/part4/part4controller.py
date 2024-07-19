# Part 4 of UWCSE's Mininet-SDN project
#
# based on Lab Final from UCSC's Networking Class
# which is based on of_tutorial by James McCauley

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, IPAddr6, EthAddr
from pox.lib.packet.arp import arp
from pox.lib.packet.ethernet import ethernet

log = core.getLogger()

# Convenience mappings of hostnames to ips
IPS = {
    "h10": "10.0.1.10",
    "h20": "10.0.2.20",
    "h30": "10.0.3.30",
    "serv1": "10.0.4.10",
    "hnotrust": "172.16.10.100",
}

# Convenience mappings of hostnames to subnets
SUBNETS = {
    "h10": "10.0.1.0/24",
    "h20": "10.0.2.0/24",
    "h30": "10.0.3.0/24",
    "serv1": "10.0.4.0/24",
    "hnotrust": "172.16.10.0/24",
}


class Part4Controller(object):
    """
    A Connection object for that switch is passed to the __init__ function.
    """

    def __init__(self, connection):
        print(connection.dpid)
        # Keep track of the connection to the switch so that we can
        # send it messages!
        self.connection = connection

        # This binds our PacketIn event listener
        connection.addListeners(self)
        # use the dpid to figure out what switch is being created
        if connection.dpid == 1:
            self.s1_setup()
        elif connection.dpid == 2:
            self.s2_setup()
        elif connection.dpid == 3:
            self.s3_setup()
        elif connection.dpid == 21:
            self.cores21_setup()
        elif connection.dpid == 31:
            self.dcs31_setup()
        else:
            print("UNKNOWN SWITCH")
            exit(1)

    def s1_setup(self):
        # put switch 1 rules here
        fm=of.ofp_flow_mod()
        fm.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
        self.connection.send(fm)

    def s2_setup(self):
        # put switch 2 rules here
        fm=of.ofp_flow_mod()
        fm.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
        self.connection.send(fm)

    def s3_setup(self):
        # put switch 3 rules here
        fm=of.ofp_flow_mod()
        fm.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
        self.connection.send(fm)

    def cores21_setup(self):
        # put core switch rules here
        # hnotrust1 cannot send ICMP traffic to h10, h20, h30, or serv1
        fm = of.ofp_flow_mod()
        fm.match.nw_src = IPS["hnotrust"]
        fm.match.nw_proto = 1
        fm.match.dl_type = 0x0800
        self.connection.send(fm)

        # hnotrust1 cannot send any IP traffic to serv1
        fm = of.ofp_flow_mod()
        fm.match.nw_src = IPS["hnotrust"]
        fm.match.dl_type = 0x0800
        fm.match.nw_dst = IPS['serv1']
        self.connection.send(fm)

    def dcs31_setup(self):
        # put datacenter switch rules here
        fm=of.ofp_flow_mod()
        fm.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
        self.connection.send(fm)

    # used in part 4 to handle individual ARP packets
    # not needed for part 3 (USE RULES!)
    # causes the switch to output packet_in on out_port
    def resend_packet(self, packet_in, out_port):
        msg = of.ofp_packet_out()
        msg.data = packet_in
        action = of.ofp_action_output(port=out_port)
        msg.actions.append(action)
        self.connection.send(msg)

    def _handle_PacketIn(self, event):
        """
        Packets not handled by the router rules will be
        forwarded to this method to be handled by the controller
        """

        packet = event.parsed  # This is the parsed packet data.
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        packet_in = event.ofp  # The actual ofp_packet_in message.
        port_number = event.port

        # dealing with ARP messages
        if packet.type == packet.ARP_TYPE:
            if packet.payload.opcode == arp.REQUEST:
                arp_reply = arp()
                arp_reply.hwsrc = EthAddr("00:00:00:00:00:01")
                arp_reply.hwdst = packet.src
                arp_reply.opcode = arp.REPLY
                arp_reply.protosrc = packet.payload.protodst
                arp_reply.protodst = packet.payload.protosrc

                # changing the ethernet header
                ether = ethernet()
                ether.type = ethernet.ARP_TYPE
                ether.dst = packet.src
                ether.src = EthAddr("00:00:00:00:00:01")
                ether.payload = arp_reply

                # IP message
                m = of.ofp_flow_mod()
                fm.match.dl_type = 0x0800
                fm.match.nw_dst = packet.payload.protosrc
                fm.actions.append(of.ofp_action_dl_addr.set_dst(packet.src))
                fm.actions.append(of.ofp_action_output(port=port_number))
                self.connection.send(fm)

                # resend the packet
                self.resend_packet(ether, port_number)

def launch():
    """
    Starts the component
    """

    def start_switch(event):
        log.debug("Controlling %s" % (event.connection,))
        Part4Controller(event.connection)

    core.openflow.addListenerByName("ConnectionUp", start_switch)
