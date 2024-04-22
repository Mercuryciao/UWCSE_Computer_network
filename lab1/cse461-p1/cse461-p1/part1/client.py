import socket
from struct import pack, unpack
import time
import sys

def main():
    try:
        domain = sys.argv[1]
        port = int(sys.argv[2])
        student_id = 575
        timeout = 3
        psecret = 0
        client_step = 1

        ## stage A
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message='hello world'+'\0'
        # >: the data should be in big-endian byte order
        # i: Represents a signed integer, typically 4 bytes in size.
        # h: Represents a signed short integer, typically 2 bytes in size.
        encoded_message = message.encode('utf-8')
        header = pack('>iihh', len(message), psecret, client_step, student_id)+encoded_message

        sock.sendto(header, (domain, port))
        try:
            sock.settimeout(timeout)
            UDP_packet = sock.recv(1024)
        except socket.error as socketerror:
            print("Error: ", socketerror)
            return
        payload_len, psecret, server_step, student_id, num, length, udp_port, secretA = unpack('>iihhiiii', UDP_packet)
        sock.close()

        ## stage B
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # byte-aligned to a 4-byte boundary: 
        # If the length is not divisible by 4, then augment it by the smallest number that is divisible by 4        
        if length % 4 != 0:
            payload = bytearray(length+(4-length%4))
        else:
            payload = bytearray(length)
        count = 0
        while count < num:
            header = pack('>iihhi', length+4, secretA, client_step, student_id, count)
            header += payload
            sock.sendto(header, (domain, udp_port))
            try:
                sock.settimeout(0.5)
                ans = sock.recv(1024)
                payload_len, psecret, server_step, student_id, acked_packet_id = unpack('>iihhi', ans)
                count+=1
            except socket.error as socketerror:
                print("Error: ", socketerror)

        try:
            sock.settimeout(5)
            res = sock.recv(1024)
        except socket.error as socketerror:
            print("Error: ", socketerror)
            return

        payload_len, psecret, server_step, student_id, tcp_port, secretB = unpack('>iihhii', res)
        sock.close()

        ## stage C
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((domain, tcp_port))
            try:
                s.settimeout(timeout)
                res = s.recv(1024)
                
            except socket.error as socketerror:
                print("Error: ", socketerror)
                return
            payload_len, psecret, server_step, student_id, num2, len2, secretC, c = unpack('>iihhiiic', res[0:25])
            print('payload_len',payload_len,'psecret', psecret,'server_step', server_step, 'student_id', 'num2', num2, 'len2', len2, 'secretC', secretC, 'c', c)

            ## stage D
            header = pack('>iihh', len2, secretC, client_step, student_id)

            # byte-aligned to a 4-byte boundary
            if len2 % 4 != 0:
                payload = c*(len2+(4-len2%4))
            else:
                payload = c*len2
            header += payload

            # sends num2 payloads
            for _ in range(num2):
                s.send(header)
            try:
                s.settimeout(timeout)
                res = s.recv(1024)
            except socket.error as socketerror:
                print("Error: ", socketerror)
                return

            payload_len, psecret, server_step, student_id, secretD = unpack('>iihhi', res)
        print('A: ', secretA, 'B: ', secretB, 'C: ', secretC, 'D: ', secretD)

    except KeyboardInterrupt:
        print("keyboard interrupt")
        sys.exit(0)

if __name__ == '__main__':
    main()