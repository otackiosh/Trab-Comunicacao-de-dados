import PySimpleGUI as sg 
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import socket

HOST = '127.0.0.1'
PORT = 16666
CHAVE = b'chave'



#BINARIO
def toBin(msg):
    msgBin = ""
    for x in range(len(msg)):
        msgBin = msgBin + format(msg[x], '08b')
    return msgBin





# 4D-PAM5
def binTo4dpam5(msgBin):
    pam5 = []
    for x in [msgBin[i:i+2] for i in range (0, len(msgBin), 2)]:
        if (x == "00"):
            pam5.append(2)
        elif (x == "01"):
            pam5.append(1)
        elif (x == "10"):
            pam5.append(-1)
        else:
            pam5.append(-2)
    return pam5



# AMI
def binToAmi(msgBin):
    ami = []
    count = 0
    for x in range(len(msgBin)):
        count = count%(-4)
        if(msgBin[x] == '1'):
            ami.append(int(msgBin[x]) + count)
            count -= 2
        else:
            ami.append(0)
    return ami


# CRIPTOGRAFIA 
def vigenereEnc(msg, chave):
    count = 0
    msgCripto = ""
    for x in msg:
        msgCripto += chr((int(format(x, 'd'))+int(format(chave[count], 'd'))) % 256)
        count += 1
        count %= len(chave)
    print(msgCripto.encode('ansi'))
    return msgCripto.encode('ansi')


#GRAFICO FIGURE
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg




#GUI
layout = [[sg.Text("Digite a mensagem")],
        [sg.Input(key='-INPUT-')],
        [sg.Text(size=(80,1), key='-MSGCRY-')],
        [sg.Text(size=(80,1), key='-MSGBIN-')],
        [sg.Text(size=(80,1), key='-MSGPAM-')],
        [sg.Canvas(key='-CANVAS-')],
        [sg.Button('Ok')]]


window = sg.Window('Emissor', layout, finalize = True)


fig, ax = plt.subplots()
fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == 'Quit':
        break
    

    msg = str(values['-INPUT-'])
    msg = msg.encode("ansi")
    
    msg = vigenereEnc(msg, CHAVE)
    window['-MSGCRY-'].update("MSGCRY: " + msg.decode("ansi"))
    

    msg = toBin(msg)
    print(msg)
    window['-MSGBIN-'].update("BIN: " + msg)

    msg = binTo4dpam5(msg)
    print(msg)
    window['-MSGPAM-'].update("PAM: " + " ".join(map(str, msg)))



    t = np.arange(0, len(msg), 1)
    ax.cla()
    ax.step(t, msg, "r", where = 'post')
    ax.set_xticks(t)
    ax.set_xticklabels([])
    ax.grid()
    fig_canvas_agg.draw()

    envMsg = str(msg)
    envMsg = envMsg.encode()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.send(envMsg)
        data = s.recv(1024)
        s.close()



window.close()

