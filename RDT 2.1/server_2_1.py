import argparse
import rdt_2_1
import time


def makePigLatin(word):
    m  = len(word)
    vowels = "a", "e", "i", "o", "u", "y"
    if m<3 or word=="the":
        return word
    else:
        for i in vowels:
            if word.find(i) < m and word.find(i) != -1:
                m = word.find(i)
        if m==0:
            return word+"way"
        else:
            return word[m:]+word[:m]+"ay"

def piglatinize(message):
    essagemay = ""
    message = message.strip(".")
    for word in message.split(' '):
        essagemay += " "+makePigLatin(word)
    return essagemay.strip()+"."


if __name__ == '__main__':
    parser =  argparse.ArgumentParser(description='Pig Latin conversion server.')
    parser.add_argument('port', help='Port.', type=int)
    args = parser.parse_args()

    timeout = 5 #close connection if no new data within 5 seconds
    time_of_last_data = time.time()

    rdt = rdt_2_1.RDT('server', None, args.port)
    print(rdt.network)
    while(True):
        #try to receive a message before timeout
        msg_S = rdt.rdt_2_1_receive()
        if msg_S is None:
            # if the server has timed out, stop listening for packets and quit server
            if time_of_last_data + timeout < time.time():
                break
            # if the server has not timed out, continue listening
            else:
                continue
        time_of_last_data = time.time()

        #convert and reply
        print("Sending ACK")
        rdt.rdt_2_1_send("ACK")
        rep_msg_S = piglatinize(msg_S)
        print('Converted %s \nto %s\n' % (msg_S, rep_msg_S))
        rdt.rdt_2_1_send(rep_msg_S)

    rdt.disconnect()
