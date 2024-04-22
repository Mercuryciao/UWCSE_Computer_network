import socket
from struct import pack, unpack
import random
import time
import threading
import sys
from _thread import *

def verify_header(message, payload_len, expected_payload_len, presecret, expected_psecret, client_step):
    # verify the header of each stage
    expected_client_step = 1
    expected_header_length = 12
    if (len(message) < expected_header_length or
        payload_len != expected_payload_len or 
        presecret != expected_psecret or 
        client_step != expected_client_step):
        return False
    else:
        return True

def stage_processing(s, address, received_data, ip):
    expected_client_step = 1
    server_step = 2
    timeout = 3
    ######## stage A ########
    try:
        payload_len, presecret, client_step, student_id = unpack('>iihh', received_data[0:12])
        payload = received_data[12:].decode('utf-8')

        # verify the header
        if (not verify_header(received_data, payload_len, len(payload), presecret, 0, client_step) or 
            payload != 'hello world'+'\0'):
            print("invalid header in stage A")
            return
        # randomly generate the response with a UDP packet containing four integers
        num = random.randint(6, 12)
        length = random.randint(5, 10)
        udp_port = random.randint(20000, 40000)
        secretA = random.randint(50, 1000)
        send_header = pack('>iihhiiii', 16, 0, server_step, student_id, num, length, udp_port, secretA)
        s.sendto(send_header, address)

        ######## stage B ########
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind((ip, udp_port))

            # calculate the padding
            if length % 4 != 0:
                expected_length = length+(4-length%4)
            else:
                expected_length = length
            count = 0
            while count < num:
                try:
                    s.settimeout(timeout)
                    message, address = s.recvfrom(1024)
                except socket.timeout:
                    print("Socket timed out in stage B.")
                    return
                
                payload_len, psecret, client_step, student_id, packet_id = unpack('>iihhi', message[0:16])
                payload = message[16:]

                # verify the header
                if not verify_header(message, payload_len, length+4, psecret, secretA, client_step) or packet_id != count or len(message) != (expected_length+16):
                    print("invalid header in stage B")
                    return 

                # verify payload content
                for i in range(length):
                    if payload[i] != 0:
                        print("invalid payload in stage B")
                        return

                # randomly send an ack
                options = [True] * 6 + [False] * 4
                send_ack = random.choice(options)
                if send_ack:
                    res = pack('>iihhi', 4, secretA, server_step, student_id, count)
                    s.sendto(res, address)
                    count += 1
            # randomly generate the response with a UDP packet containing two integers
            tcp_port =  random.randint(40000, 50000)
            secretB = random.randint(100, 1000)

            # send the secretB after receive the last packet
            res = pack('>iihhii', 8, secretA, server_step, student_id, tcp_port, secretB)
            s.sendto(res, address)

        ######## stage C ########
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(timeout)
            sock.bind((ip, tcp_port))
        except socket.timeout:
            print("Socket timed out in stage C.")
            return
        sock.listen()
        conn, address = sock.accept()
        # randomly generate the response with three integers: num2, len2, secretC, and a character
        num2 = random.randint(10, 30)
        len2 = random.randint(10, 30)
        secretC = random.randint(60, 100)
        c = chr(random.randint(60, 100))
        # add the padding
        c_padding = c + '000'
        res = pack('>iihhiii', 13 , secretB, server_step, student_id, num2, len2, secretC)
        res += c_padding.encode('ascii')
        conn.sendto(res, address)

        ######## stage D ########
        # calculate the padding
        if len2 % 4 != 0:
            expected_message_len = 12+len2+(4-len2%4)
        else:
            expected_message_len = 12+len2
        expected_payload = c * len2

        num_received = 0
        while num_received < num2:
            try:
                conn.settimeout(timeout)
                res = conn.recv(expected_message_len)
            except socket.timeout:
                print("Socket timed out in stage D.")
                return
            payload_len, psecret, client_step, student_id = unpack('>iihh', res[0:12])
            payload = res[12:12+len2]
            # verify the header
            if not verify_header(res, payload_len, len2, psecret, secretC, client_step):
                print("invalid header in stage D")
                return
            if payload.decode('ascii') != expected_payload:
                print("invalid character in stage D")
                return
            num_received+=1
        # randomly generate the response with one integer secretD
        secretD = random.randint(50, 100)
        res = pack('>iihhi', 4, secretC, server_step, student_id, secretD)
        conn.sendto(res, address)
        print('secretD', secretD)
        sock.close()
    except KeyboardInterrupt:
        print("keyboard interrupt")
        sys.exit(0)

def main():
    try:
        ip = sys.argv[1]
        udp_port = int(sys.argv[2])
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind((ip, udp_port))

            while True:
                try:
                    s.settimeout(10)
                    received_data, address = s.recvfrom(1024)
                except socket.timeout:
                    print("main socket timeout")
                    return
                start_new_thread(stage_processing, (s, address, received_data, ip))

    except KeyboardInterrupt:
        print("keyboard interrupt")
        sys.exit(0)


if __name__ == '__main__':
    main()