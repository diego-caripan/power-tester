import socket
import json
import subprocess as sub
# import os
# import sys
import time

HOST = '192.168.56.1'  # The server's hostname or IP address
PORT = 50000        # The port used by the server


while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
        except ConnectionRefusedError:
            print('Waiting for connection')         # agregar limite de intentos
            time.sleep(5)
            continue
        payload = b''
        while True:
            try:
                data = s.recv(1024)
                if not data:
                    break
            except ConnectionResetError:
                break
            payload += data
        payloadDict = json.loads(payload.decode())
        nameRequest = payloadDict["name"]
        name = nameRequest + ".cpp"
        with open(name, 'w') as f:
            f.write(payloadDict["code"])

    print('Received', payloadDict["name"])


    # ejecutar script de pruebas
    sub.run(["g++", name], universal_newlines=True)  # agregar optimizaciones
    try:
        aux = sub.run(["bash", "measurescript.sh", "a.out"], capture_output=True, universal_newlines=True, timeout=45)
    except sub.TimeoutExpired:
        # ver que hacer en caso de error
        pass
    resultname = aux.stdout
    resultname = resultname.strip()

    PORT2 = 60000

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
        s2.connect((HOST, PORT2))
        with open(resultname, 'r') as f:
            results = f.read()
        m = {"name": nameRequest + "Results", "results": results}
        json_string = json.dumps(m)
        s2.sendall(json_string.encode())

    print('Sent', m["name"])

    sub.run(["rm", resultname, name, 'a.out'], timeout=15)
    time.sleep(10)
