from packet import Packet
from socket import *
import argparse

emulator_addr = None
emulator_port = None
receiver_port = None
output_file = None

buffer = {}
type = None
data = None
seqnum = None
seqnum_counter = 0 # packet seqnum should expect

SACK = 0
Data = 1
EOT = 2

def log_arrival(seqnum):
    with open("arrival.log", "a") as file:
        file.write(f"{seqnum}\n")

def clear_log():
    with open('arrival.log', 'w') as file:
        file.write('')
    with open(output_file, 'w') as file:
        file.write('')

if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("<emulator hostname>", help="hostname for the network emulator")
    parser.add_argument("<emulator port>", help="UDP port number used by the link emulator to receive ACKs from the receiver")
    parser.add_argument("<receiver port>", help="UDP port number used by the receiver to receive data from the emulator")
    parser.add_argument("<output file>", help="name of the file into which the received data is written")
    args = parser.parse_args()
    args = args.__dict__
    emulator_addr = str(args["<emulator hostname>"])
    emulator_port = int(args["<emulator port>"])
    receiver_port = int(args["<receiver port>"])
    output_file = args["<output file>"]

    clear_log()

    receiverSocket = socket(AF_INET, SOCK_DGRAM)
    receiverSocket.bind(('', receiver_port))

    while True:
        packet, addr = receiverSocket.recvfrom(2048)
        type, seqnum, length, data = Packet(packet).decode()

        if type == EOT:
            log_arrival("EOT")
        else:
            log_arrival(seqnum)

        if type == EOT and seqnum == seqnum_counter: # EOT packet
            eot_packet = Packet(EOT, seqnum_counter, 0, '')
            receiverSocket.sendto(eot_packet.encode(), (emulator_addr, emulator_port))
            receiverSocket.close()
            print("File receive complete.")
            break
        elif type == Data: # Data packet
            if (seqnum >= seqnum_counter and seqnum < seqnum_counter + 10) or (seqnum < seqnum_counter and abs(seqnum - seqnum_counter) > 10): # within the receiver window
                sack_packet = Packet(SACK, seqnum, 0, '')
                receiverSocket.sendto(sack_packet.encode(), (emulator_addr, emulator_port))
                if not seqnum in buffer:
                    buffer[seqnum] = data # add packet to buffer
                while seqnum_counter in buffer: # read from buffer, remove the packets that are in order
                    with open(output_file, 'a') as output:
                        output.write(buffer[seqnum_counter])
                    buffer.pop(seqnum_counter)
                    seqnum_counter = (seqnum_counter + 1) % 32
            elif (seqnum > seqnum_counter and abs((seqnum + 10)%32 - seqnum_counter) < 10) or (seqnum < seqnum_counter and abs(seqnum - seqnum_counter) < 10): # within last 10 of the base
                sack_packet = Packet(SACK, seqnum, 0, '')
                receiverSocket.sendto(sack_packet.encode(), (emulator_addr, emulator_port))
                