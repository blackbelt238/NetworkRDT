import network_2_1
import argparse
from time import sleep
import hashlib

class Packet:
    ## the number of bytes used to store packet length
    seq_num_S_length = 10
    length_S_length = 10
    ## length of md5 checksum in hex
    checksum_length = 32

    def __init__(self, seq_num, msg_S):
        self.seq_num = seq_num
        self.msg_S = msg_S
        # since checksum is implicit, no checksum field here

    @classmethod
    def from_byte_S(self, byte_S):
        if Packet.corrupt(byte_S):
            raise RuntimeError('Cannot initialize Packet: byte_S is corrupt')
        #extract the fields
        seq_num = int(byte_S[Packet.length_S_length : Packet.length_S_length+Packet.seq_num_S_length])
        msg_S = byte_S[Packet.length_S_length+Packet.seq_num_S_length+Packet.checksum_length :]
        return Packet(seq_num, msg_S)

    def get_byte_S(self):
        #convert sequence number of a byte field of seq_num_S_length bytes
        seq_num_S = str(self.seq_num).zfill(self.seq_num_S_length)
        #convert length to a byte field of length_S_length bytes
        length_S = str(self.length_S_length + len(seq_num_S) + self.checksum_length + len(self.msg_S)).zfill(self.length_S_length)
        #compute the checksum
        checksum = hashlib.md5((length_S+seq_num_S+self.msg_S).encode('utf-8'))
        checksum_S = checksum.hexdigest()
        #compile into a string
        return length_S + seq_num_S + checksum_S + self.msg_S

    @staticmethod
    def corrupt(byte_S):
        #extract the fields
        length_S = byte_S[0:Packet.length_S_length]
        seq_num_S = byte_S[Packet.length_S_length : Packet.seq_num_S_length+Packet.seq_num_S_length]
        checksum_S = byte_S[Packet.seq_num_S_length+Packet.seq_num_S_length : Packet.seq_num_S_length+Packet.length_S_length+Packet.checksum_length]
        msg_S = byte_S[Packet.seq_num_S_length+Packet.seq_num_S_length+Packet.checksum_length :]

        #compute the checksum locally
        checksum = hashlib.md5(str(length_S+seq_num_S+msg_S).encode('utf-8'))
        computed_checksum_S = checksum.hexdigest()
        #and check if the same
        return checksum_S != computed_checksum_S

    def isACK(msg):
        return msg == "ACK"

    def isNAK(msg):
        return msg == "NAK"

class RDT:
    ## latest sequence number used in a packet
    seq_num = 1
    ## buffer of bytes read from network
    byte_buffer = ''

    def __init__(self, role_S, server_S, port):
        self.network = network_2_1.NetworkLayer(role_S, server_S, port)

    def disconnect(self):
        self.network.disconnect()

    def rdt_1_0_send(self, msg_S):
        p = Packet(self.seq_num, msg_S)
        self.seq_num += 1
        self.network.udt_send(p.get_byte_S())

    def rdt_1_0_receive(self):
        ret_S = None
        byte_S = self.network.udt_receive()
        self.byte_buffer += byte_S
        #keep extracting packets - if reordered, could get more than one
        while True:
            #check if we have received enough bytes
            if(len(self.byte_buffer) < Packet.length_S_length):
                return ret_S #not enough bytes to read packet length
            #extract length of packet
            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) < length:
                return ret_S #not enough bytes to read the whole packet
            #create packet from buffer content and add to return string
            p = Packet.from_byte_S(self.byte_buffer[0:length])
            ret_S = p.msg_S if (ret_S is None) else ret_S + p.msg_S
            #remove the packet bytes from the buffer
            self.byte_buffer = self.byte_buffer[length:]
            #if this was the last packet, will return on the next iteration

    # sends a packet based on the RDT 2.1 protocol
    def rdt_2_1_send(self, msg_S):
        # create the packet and perform the initial send
        p = Packet(self.seq_num, msg_S)

        cur_seq = self.seq_num
        while(cur_seq >= self.seq_num):
            self.network.udt_send(p.get_byte_S())
            #print("waiting...")
            recieved_byte_str = ''
            while(recieved_byte_str == ''):
                recieved_byte_str = self.network.udt_receive()
            #self.byte_buffer += recieved_byte_str
            length = int(recieved_byte_str[:Packet.length_S_length])
            #remove the packet bytes from the buffer
            self.byte_buffer = recieved_byte_str[length:]
            pRec = Packet.from_byte_S(recieved_byte_str[:length])
            # continue on if a positive acknowledgement is recieved
            if Packet.isACK(pRec.msg_S):
                #print("ACK recieved")
                self.seq_num += 1
            # resend if a negative acknowledgement is recieved
            elif Packet.isNAK(pRec.msg_S):
                #print("NAK recieved. Resending...")
                self.byte_buffer = ''

    # recieves a packet based on the RDT 2.1 protocol
    def rdt_2_1_receive(self):
        ret_S = None
        byte_S = self.network.udt_receive()
        self.byte_buffer += byte_S
        #keep extracting packets - if reordered, could get more than one
        while True:
            #check if we have received enough bytes
            if(len(self.byte_buffer) < Packet.length_S_length):
                return ret_S #not enough bytes to read packet length
            #extract length of packet
            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) < length:
                return ret_S #not enough bytes to read the whole packet
            #create packet from buffer content and add to return string
            p = Packet.from_byte_S(self.byte_buffer[0:length])

            # if a recieved packet has been corrupted, attempt to collect packets
            if Packet.corrupt(p.get_byte_S()):
                #print("Sending NAK")
                pak = Packet(self.seq_num, "NAK")
                self.network.udt_send(pak.get_byte_S())
                self.byte_buffer = ""
                return None
            else:
                pak = Packet(self.seq_num, "ACK")
                self.network.udt_send(pak.get_byte_S())

            ret_S = p.msg_S if (ret_S is None) else ret_S + p.msg_S
            #remove the packet bytes from the buffer
            self.byte_buffer = self.byte_buffer[length:]
            #if this was the last packet, will return on the next iteration

    def rdt_3_0_send(self, msg_S):
        pass

    def rdt_3_0_receive(self):
        pass


if __name__ == '__main__':
    parser =  argparse.ArgumentParser(description='RDT implementation.')
    parser.add_argument('role', help='Role is either client or server.', choices=['client', 'server'])
    parser.add_argument('server', help='Server.')
    parser.add_argument('port', help='Port.', type=int)
    args = parser.parse_args()

    rdt = RDT(args.role, args.server, args.port)
    if args.role == 'client':
        rdt.rdt_2_1_send('MSG_FROM_CLIENT')
        sleep(2)
        print(rdt.rdt_2_1_receive())
        rdt.disconnect()

    else:
        sleep(1)
        print(rdt.rdt_2_1_receive())
        rdt.rdt_2_1_send('MSG_FROM_SERVER')
        rdt.disconnect()
