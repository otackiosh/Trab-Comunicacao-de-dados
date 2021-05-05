import PySimpleGUI as sg
import socket
import threading
import sys
from multiprocessing import Process
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.use('TkAgg')
import codecs

HOST = '127.0.0.1'
PORT = 16666
CHAVE = b'chave'

#GRAFICO FIGURE
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def pam5ToBin(msg):
    msgBin = []
    for x in msg:
        if (x == -2):
            msgBin.append('1');msgBin.append('1')
        elif(x == -1):
            msgBin.append('1');msgBin.append('0')
        elif(x == 1):
            msgBin.append('0');msgBin.append('1')
        else:
            msgBin.append('0');msgBin.append('0')
    return msgBin

def amiToBin(msg):
    msgBin = []
    for x in msg:
        if (x == 0):
            msgBin.append('0')
        else:
            msgBin.append('1')
    return msgBin

def decoder(s):
    u = "".join([chr((int(x,2))) for x in [s[i:i+8] 
                           for i in range(0,len(s), 8)
                           ]
            ])
    return u

def vigenereDec(msg, chave):
    count = 0
    msgCripto = ""
    for x in msg:
        msgCripto += chr((int(format(x, 'd'))-int(format(chave[count], 'd'))) % 256)
        count += 1
        count %= len(chave)
    return msgCripto

def servidor(window):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        print("server aberto")
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                global data
                data = conn.recv(1024)
                window.write_event_value('-UPDATE DATA-', '')
                conn.sendall(data)
                conn.close()


if __name__ == '__main__':
    layout =[[sg.Text(size=(80,1), key='-MSGPAM-')],
            [sg.Text(size=(80,1), key='-MSGBIN-')],
            [sg.Text(size=(80,1), key='-MSGCRY-')],
            [sg.Text(size=(80,1), key='-MSG-')],
            [sg.Canvas(key='-CANVAS-')],
            [sg.Button('Exit')]]


    window = sg.Window('Receptor', layout, finalize = True)

    fig, ax = plt.subplots()
    fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)


    processServer = threading.Thread(target = servidor, args = (window, ))
    processServer.start()


    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break
        if event == '-UPDATE DATA-':

            msg = eval(data.decode('utf-8'))

            t = np.arange(0, len(msg), 1)
            ax.cla()
            ax.step(t, msg, "r", where = 'post')
            ax.set_xticks(t)
            ax.set_xticklabels([])
            ax.grid()
            fig_canvas_agg.draw()

            window['-MSGPAM-'].update("PAM: " + " ".join(map(str, msg)))

            msg = pam5ToBin(msg)
            window['-MSGBIN-'].update("BIN: " + "".join(msg))


            msg = "".join(msg)
            msg = decoder(msg)
            window['-MSGCRY-'].update("MSGCRY: " + msg)

            msg = msg.encode("ansi")
            msg = vigenereDec(msg, CHAVE)
            window['-MSG-'].update("MSG: " + msg)


    window.close()
    sys.exit()