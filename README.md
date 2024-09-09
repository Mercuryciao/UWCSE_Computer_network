# CSE_computer_network

## Lab 1: Socket Programming
Implement both a client and a server that follow a defined protocol for communication. The client extracts secrets from the server at each stage, while the server validates the client's adherence to the protocol and responds accordingly. Proper handling of both UDP and TCP protocols, packet validation, and error handling are key aspects of this lab.

## Lab 2: Link and Network with Software Defined Networking

### Part 1: Mininet Primer
Use Mininet, a network emulator, and create a simple network topology using Python. 

### Part 2: SDN Controllers Using POX
Create a simple firewall using the POX SDN controller to control traffic. The goal is to:

Allow ICMP and ARP traffic to pass through the switch.
Block all other types of IP traffic.

### Part 3: A Real Network
Expande on the firewall implementation to simulate a company network with multiple subnets and a core switch. The goal is to:

Ensure all nodes can communicate with each other except for specific restrictions on traffic from an untrusted host.
Block certain types of traffic, such as IP and ICMP, between specified hosts.

### Part 4: A Learning Router
Enhance the network by making the core switch (router) capable of routing IP traffic between subnets. The goal is to:

Handling ARP requests dynamically.
Forwarding IP traffic between different subnets while learning routes dynamically through ARP messages.

## Lab 3: HTTP Proxy
Developed a multi-threaded HTTP proxy capable of handling both standard HTTP requests (e.g., GET, POST) and HTTP CONNECT tunneling. Our proxy will act as an intermediary between web clients (e.g., browsers) and web servers, forwarding requests from clients to servers and sending back the responses from servers to clients. The proxy will also be able to handle HTTPS connections using the CONNECT method by establishing a TCP connection between the client and the server and relaying data back and forth.
