# This is a sample Python script.

from Interface import Interface
from tkinter import *

def eventModos(event):
    if(a.comboModo.get() == 'Constante'):
        a.entryCorrente['state'] = 'disabled'
        a.entryDuty['state'] = 'normal'
        a.entryTempo['state'] = 'disabled'


    elif(a.comboModo.get() == 'Corrente Constante'):
        a.entryCorrente['state'] = 'normal'
        a.entryDuty['state'] = 'disabled'
        a.entryTempo['state'] = 'disabled'

    elif (a.comboModo.get() == 'Timer Constante'):
        a.entryCorrente['state'] = 'disabled'
        a.entryDuty['state'] = 'normal'
        a.entryTempo['state'] = 'normal'

    elif (a.comboModo.get() == 'Timer Corrente Constante'):
        a.entryCorrente['state'] = 'normal'
        a.entryDuty['state'] = 'disabled'
        a.entryTempo['state'] = 'normal'

def eventEnviarSerial(event):
    a.botao_enviarSerial()
# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    root = Tk()
    a = Interface(master=root)
    eventModos('')
    a.comboModo.bind("<<ComboboxSelected>>", eventModos)
    a.entryTerminal.bind('<Any-KeyPress-Return>', eventEnviarSerial)
    root.iconbitmap(r'Images/logo.ico')
    root.title('Interface')
    root.geometry('930x600')
    root.resizable(width=0, height=0)
    root.after(1, a.lerSerial)
    root.mainloop()

