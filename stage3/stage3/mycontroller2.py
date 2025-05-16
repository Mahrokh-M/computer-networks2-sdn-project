from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp, arp

class QoSLoadBalancer(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(QoSLoadBalancer, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id

        # Default flow: Drop
        match = parser.OFPMatch()
        actions = []
        self.add_flow(datapath, 0, match, actions)

        # Traffic routing
        if dpid == 2:  # s2
            # HTTP from h1 to h3/h4
            match_http = parser.OFPMatch(eth_type=0x0800, ip_proto=6, tcp_dst=80, in_port=2)
            actions_http = [parser.OFPActionOutput(3)]  # to s4
            self.add_flow(datapath, 10, match_http, actions_http)
            # HTTP back from h3/h4 to h1
            match_http_back = parser.OFPMatch(eth_type=0x0800, ip_proto=6, tcp_src=80, in_port=3)
            actions_http_back = [parser.OFPActionOutput(2)]  # to h1
            self.add_flow(datapath, 10, match_http_back, actions_http_back)

            # SSH from h1 to h2
            match_ssh = parser.OFPMatch(eth_type=0x0800, ip_proto=6, tcp_dst=22, in_port=2)
            actions_ssh = [parser.OFPActionOutput(1)]  # to s1
            self.add_flow(datapath, 10, match_ssh, actions_ssh)
            # SSH back from h2 to h1
            match_ssh_back = parser.OFPMatch(eth_type=0x0800, ip_proto=6, tcp_src=22, in_port=1)
            actions_ssh_back = [parser.OFPActionOutput(2)]  # to h1
            self.add_flow(datapath, 10, match_ssh_back, actions_ssh_back)

            # iperf from h1 to h2
            match_iperf = parser.OFPMatch(eth_type=0x0800, ip_proto=6, tcp_dst=5001, in_port=2)
            actions_iperf = [parser.OFPActionOutput(1)]  # to s1
            self.add_flow(datapath, 10, match_iperf, actions_iperf)
            # iperf back from h2 to h1
            match_iperf_back = parser.OFPMatch(eth_type=0x0800, ip_proto=6, tcp_src=5001, in_port=1)
            actions_iperf_back = [parser.OFPActionOutput(2)]  # to h1
            self.add_flow(datapath, 10, match_iperf_back, actions_iperf_back)

        elif dpid == 1:  # s1
            # SSH from s2 to s3
            match_ssh = parser.OFPMatch(eth_type=0x0800, ip_proto=6, tcp_dst=22, in_port=1)
            actions_ssh = [parser.OFPActionOutput(2)]  # to s3
            self.add_flow(datapath, 10, match_ssh, actions_ssh)
            # SSH back from s3 to s2
            match_ssh_back = parser.OFPMatch(eth_type=0x0800, ip_proto=6, tcp_src=22, in_port=2)
            actions_ssh_back = [parser.OFPActionOutput(1)]  # to s2
            self.add_flow(datapath, 10, match_ssh_back, actions_ssh_back)

            # iperf from s2 to s3
            match_iperf = parser.OFPMatch(eth_type=0x0800, ip_proto=6, tcp_dst=5001, in_port=1)
            actions_iperf = [parser.OFPActionOutput(2)]  # to s3
            self.add_flow(datapath, 10, match_iperf, actions_iperf)
            # iperf back from s3 to s2
            match_iperf_back = parser.OFPMatch(eth_type=0x0800, ip_proto=6, tcp_src=5001, in_port=2)
            actions_iperf_back = [parser.OFPActionOutput(1)]  # to s2
            self.add_flow(datapath, 10, match_iperf_back, actions_iperf_back)

        elif dpid == 3:  # s3
            # SSH from s1 to h2
            match_ssh = parser.OFPMatch(eth_type=0x0800, ip_proto=6, tcp_dst=22, in_port=1)
            actions_ssh = [parser.OFPActionOutput(2)]  # to h2
            self.add_flow(datapath, 10, match_ssh, actions_ssh)
            # SSH back from h2 to s1
            match_ssh_back = parser.OFPMatch(eth_type=0x0800, ip_proto=6, tcp_src=22, in_port=2)
            actions_ssh_back = [parser.OFPActionOutput(1)]  # to s1
            self.add_flow(datapath, 10, match_ssh_back, actions_ssh_back)

            # iperf from s1 to h2
            match_iperf = parser.OFPMatch(eth_type=0x0800, ip_proto=6, tcp_dst=5001, in_port=1)
            actions_iperf = [parser.OFPActionOutput(2)]  # to h2
            self.add_flow(datapath, 10, match_iperf, actions_iperf)
            # iperf back from h2 to s1
            match_iperf_back = parser.OFPMatch(eth_type=0x0800, ip_proto=6, tcp_src=5001, in_port=2)
            actions_iperf_back = [parser.OFPActionOutput(1)]  # to s1
            self.add_flow(datapath, 10, match_iperf_back, actions_iperf_back)

        elif dpid == 4:  # s4
            # HTTP from s2 to h3/h4
            match_http = parser.OFPMatch(eth_type=0x0800, ip_proto=6, tcp_dst=80, in_port=1)
            actions_http = [parser.OFPActionOutput(2), parser.OFPActionOutput(3)]  # to h3 and h4
            self.add_flow(datapath, 10, match_http, actions_http)
            # HTTP back from h3/h4 to s2
            match_http_back_h3 = parser.OFPMatch(eth_type=0x0800, ip_proto=6, tcp_src=80, in_port=2)
            actions_http_back_h3 = [parser.OFPActionOutput(1)]  # to s2
            self.add_flow(datapath, 10, match_http_back_h3, actions_http_back_h3)
            match_http_back_h4 = parser.OFPMatch(eth_type=0x0800, ip_proto=6, tcp_src=80, in_port=3)
            actions_http_back_h4 = [parser.OFPActionOutput(1)]  # to s2
            self.add_flow(datapath, 10, match_http_back_h4, actions_http_back_h4)

        # ICMP and ARP flows
        match_icmp = parser.OFPMatch(eth_type=0x0800, ip_proto=1)
        actions_icmp = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        self.add_flow(datapath, 5, match_icmp, actions_icmp)

        match_arp = parser.OFPMatch(eth_type=0x0806)
        actions_arp = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        self.add_flow(datapath, 5, match_arp, actions_arp)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath,
            priority=priority,
            match=match,
            instructions=inst,
            buffer_id=ofproto.OFP_NO_BUFFER
        )
        datapath.send_msg(mod)
        self.logger.info("Installing flow: match=%s actions=%s", match, actions)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        if eth.ethertype == 0x88cc:  # LLDP
            return

        self.logger.info("Packet in from switch %s (port %s)", datapath.id, in_port)

        # Detect anomaly (UDP Flood)
        self.detect_anomaly(datapath, pkt)

        # Learn MAC
        dst = eth.dst
        src = eth.src
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port

        out_port = self.mac_to_port[dpid].get(dst, ofproto.OFPP_FLOOD)
        actions = [parser.OFPActionOutput(out_port)]

        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            self.add_flow(datapath, 1, match, actions)

        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=msg.data if msg.buffer_id == ofproto.OFP_NO_BUFFER else None
        )
        datapath.send_msg(out)

    def detect_anomaly(self, datapath, pkt):
        ipv4_pkt = pkt.get_protocol(ipv4.ipv4)
        if not ipv4_pkt or ipv4_pkt.proto != 17:
            return

        self.logger.info("Potential UDP Flood detected from %s", ipv4_pkt.src)
        parser = datapath.ofproto_parser
        match = parser.OFPMatch(eth_type=0x0800, ip_proto=17, ipv4_src=ipv4_pkt.src)
        actions = []
        self.add_flow(datapath, 100, match, actions)


    def block_malicious_traffic(self, datapath):
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser

    # Match packets from h3's MAC address
    match = parser.OFPMatch(eth_src="00:00:00:00:00:03")
    # Action: Drop the packet (empty actions list means drop)
    actions = []
    # Add flow rule with high priority
    self.add_flow(datapath, priority=100, match=match, actions=actions)
