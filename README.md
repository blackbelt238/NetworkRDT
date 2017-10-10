# NetworkRDT
During this project, you will implement the Reliable Data Transmission protocols RDT 2.1, and RDT 3.0 discussed in class and the textbook by extending an RDT 1.0 implementation.

### Starting Code
The starting code for this project (prog2.zip in the D2L content area) provides you with the implementation of several network layers that cooperate to provide end-to-end communication.

APPLICATION LAYER (**client.py**, **server.py**)
TRANSPORT LAYER (**rdt.py**)
NETWORK LAYER (**network.py**)

The client sends messages to the server, which converts them to pig latin, and transmits them back. The client and the server send messages to each other through the transport layer provided by an RDT implementation using the **rdt_1_0_send** and **rdt_1_0_receive** functions. The starting **rdt.py** provides only the RDT 1.0 version of the protocol, which does not tolerate packet corruption, or loss. The RDT protocol uses **udt_send** and **udt_receive** provided by **network.py** to transfer bytes between the client and server machines. The network layer may corrupt packets or lose packets altogether. **rdt.py** relies on the **Packet** class (in the same ﬁle) to form transport layer packets. Your job will be to extend **rdt.py** to tolerate packet corruption and loss. The provided code lists prototype send and receive functions for those protocols. You may need to modify/extend the **Packet** class to transmit the necessary information for these functions to work correctly. The provided implementation of **network.py** is reliable, but we will test your code with non-zero probability for packet corruption and loss by changing the values of prob_pkt_loss and prob_byte_corr of the **NetworkLayer** class. You may change those variables yourself to test your code.

### Program Invocation
To run the starting code you may run:
`python server.py 5000`
and
`python client.py localhost 5000`
in separate terminal windows. Be sure to start the server ﬁrst, to allow it to start listening on a socket, and start the client soon after, before the server times out.

### What to Submit
You will submit different versions of **rdt.py**, which implements the send and receive functions for RDT 2.1, and RDT 3.0. RDT 2.1 tolerates corrupted packets through retransmission. RDT 3.0 tolerates corrupted and lost packets through retransmission. The necessary functions prototypes are already included in **rdt.py**. For the purposes of testing you may modify **client.py** and **server.py** to use these functions instead of those of RDT 1.0. You will also submit a link to a YouTube video showing an execution of your code for each version of the protocol.
\tWe will grade the this assignment as follows:
1. [2 points] partners.txt with your partner’s, or partners’ ﬁrst and last name.
2. [10 points] rdt 2 1.py, client 2 1.py, server 2 1.py, network 2 1.py that correctly implement RDT 2.1 and a link to a YouTube video showing the execution of your program
3. [13 points] rdt 3 0.py, client 3 0.py, server 3 0.py, network 3 0.py that correctly implement RDT 3.0 and a link to a YouTube video showing the execution of your program
4. [1 point] (BONUS 1) rdt 3 1.py, client 3 1.py, server 3 1.py, network 3 1.py that correctly implement RDT 3.1 and a link to a YouTube video showing the execution of your program
5. [1 point] (BONUS 2) rdt 4 0.py, client 4 0.py, server 4 0.py, network 4 0.py that correctly implement RDT 4.0 and a link to a YouTube video showing the execution of your program
