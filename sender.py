from packet import Packet
from socket import *
from queue import Queue
import argparse
import threading

timestamp = 0
seqnum = 0
buffer = Queue()
ACK = []
data = 'something'
N = 1
type = None
length = None
packet = None
emulator_addr = None
emulator_port = None
sender_port = None
timeout = None
input_file = None
eot_early = False

SACK = 0
Data = 1
EOT = 2

seqnum_lock = threading.Lock()
ack_lock = threading.Lock()
N_lock = threading.Lock()
send_lock = threading.Lock()
receive_lock = threading.Lock()
buffer_lock = threading.Lock()
ACK_lock = threading.Lock()


def log_seqnum(seqnum):
    global timestamp
    with open("seqnum.log", "a") as file:
        file.write(f"t={timestamp} {seqnum}\n")

def log_ack(seqnum):
    global timestamp
    with open("ack.log", "a") as file:
        file.write(f"t={timestamp} {seqnum}\n")

def log_N(N: int):
    global timestamp
    with open("N.log", "a") as file:
        file.write(f"t={timestamp} {N}\n")

def time_up(timeup: bool): # timer function
    global timestamp
    timeup = True
    timestamp += 1 # increment if timeout
    return

def send(packet: Packet):
    global timestamp
    global N
    global eot_early
    timeup = False
    timer = threading.Timer(float(timeout/1000), time_up, args=(timeup,)) # if timeout
    with send_lock:
        senderSocket.sendto(packet.encode(), (emulator_addr, emulator_port)) # send packet
        with seqnum_lock:
            log_seqnum(packet.seqnum)
            timestamp += 1

    receive_thread = threading.Thread(target=receive, args=(packet.seqnum, timer)) # check if ACK is received by other threads
    ack = None
    block = False

    senderSocket.settimeout(float(timeout/1000)) # set timeout for socket.recvfrom
    with receive_lock:
        timer.start()
        receive_thread.start()
        try:
            ack, addr = senderSocket.recvfrom(2048)
        except:
            pass

    if ack != None:
        block = True
    if block:
        type, seq, length, any = Packet(ack).decode()
        if type == SACK and seq == packet.seqnum and not buffer.empty() and seq == buffer.queue[0]: # check if is ACK of oldest packet and also the current packet
            timer.cancel() # kill the thread, do not need to retransmit
            with buffer_lock:
                buffer.get() # remove the oldest packet in the buffer, first item of queue
                with ack_lock:
                    log_ack(seq) # update log
                    if N < 10: # update log if N < 10
                        with N_lock:
                            N += 1
                            log_N(N)
                    timestamp += 1

            ack_match_thread = threading.Thread(target=ack_match, args=())
            ack_match_thread.start()
            return
        elif type == SACK and seq == packet.seqnum: # check if is the ACK of current packet but not the oldest packet unACKed
            timer.cancel()
            with ack_lock:
                log_ack(seq)
                timestamp += 1
                with ACK_lock:
                    for i in range(len(ACK)): # check if is duplicate and remove
                        if ACK[i] == seq:
                            ACK.remove(seq)
                            break
                    if not buffer.empty() and (seq >= buffer.queue[0].seqnum or abs(buffer.queue[0].seqnum - seq) > 10):
                        ACK.append(seq)
            return
        elif type == SACK and seq != packet.seqnum: # other ACK
            with ack_lock:
                log_ack(seq)
                with ACK_lock:
                    for i in range(len(ACK)): # check if is duplicate and remove
                        if ACK[i] == seq:
                            ACK.remove(seq)
                            break
                    if not buffer.empty() and (seq >= buffer.queue[0].seqnum or abs(buffer.queue[0].seqnum - seq) > 10):
                        ACK.append(seq)
        elif type == EOT:
            eot_early = True
            return

def receive(ack_find: int, timer: threading.Timer): # check if ACK is received by other thread already
    while timer.is_alive() and len(ACK) > 0: # timer is not over
        if not buffer.empty() and buffer.queue[0].seqnum == ack_find: # remove only if is the oldest packet
            find = True
            with ACK_lock:
                with buffer_lock:
                    try:
                        ACK.index(ack_find)
                    except:
                        find = False
                    if find:
                        buffer.get()
                        ACK.remove(ack_find)
                    ack_match_thread = threading.Thread(target=ack_match, args=())
                    ack_match_thread.start()
                timer.cancel()
                return

def retransmit():
    global N
    global timestamp
    N = 1 # reset N to 1
    with N_lock:
        log_N(N) # update log
        # seqnum log for retransmit is done in send()
        timestamp += 1

    send(buffer.queue[0]) # retransmit
    return

def ack_match(): # clear the packets at the front of the buffer that are ACKed
    global N
    global timestamp
    match = True
    while match: # keep removing packet from buffer if ACKed
        match = False
        with ACK_lock:
            with buffer_lock:
                for i in range(len(ACK)):
                    if not buffer.empty() and buffer.queue[0].seqnum == ACK[i]: # the oldest packet ACKed
                        temp_packet = buffer.get() # remove the oldest packet
                        if N < 10:
                            with N_lock:
                                N += 1
                                log_N(N)
                                timestamp += 1
                        ACK.remove(temp_packet.seqnum) # remove ACK
                        match = True
                        break

def clear_log():
    with open('seqnum.log', 'w') as file:
        file.write('')
    with open('ack.log', 'w') as file:
        file.write('')
    with open('N.log', 'w') as file:
        file.write('')


if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("<emulator host address>", help="host address of the network emulator")
    parser.add_argument("<emulator port>", help="UDP port number used by the emulator to receive data from the sender")
    parser.add_argument("<sender port>", help="UDP port number used by the sender to receive SACKs from the emulator")
    parser.add_argument("<timeout>", help="timeout interval in units of millisecond")
    parser.add_argument("<input file>", help="name of the file to be transferred")
    args = parser.parse_args()
    args = args.__dict__
    emulator_addr = str(args["<emulator host address>"])
    emulator_port = int(args["<emulator port>"])
    sender_port = int(args["<sender port>"])
    timeout = int(args["<timeout>"])
    input_file = args["<input file>"]

    clear_log()

    senderSocket = socket(AF_INET, SOCK_DGRAM)
    senderSocket.bind(('', sender_port))

    with N_lock:
        log_N(N)
        timestamp += 1

    with open(input_file, 'r') as input:
        while data != '': # still txt to send
            if buffer.qsize() < N: # window not full
                data = input.read(500)
                packet = Packet(1, seqnum, len(data), data)
                buffer.put(packet)
                seqnum = (seqnum+1) % 32
                send_thread = threading.Thread(target=send, args=(packet,))
                send_thread.start()
                
            else:
                ack_match()
                if not buffer.empty():
                    retransmit()
        
    while buffer.qsize() > 0:
        retransmit()

    # all the packets sent and ACKed
    eot_packet = Packet(EOT, seqnum, 0, '')
    with send_lock:
        senderSocket.sendto(eot_packet.encode(), (emulator_addr, emulator_port))
        with seqnum_lock:
            log_seqnum("EOT")
            timestamp += 1

    temp = threading.Timer(0.1, time_up, args=(True,))
    temp.start()
    temp.join()

    senderSocket.settimeout(float(timeout/1000))
    with receive_lock:
        try:
            packet, addr = senderSocket.recvfrom(2048)
        except:
            pass
    if not eot_early:
        type, seq, length, any = Packet(packet).decode()
    with ack_lock:
        log_ack("EOT")
        timestamp += 1

    senderSocket.close()
    print("File send complete.")
