import tkinter as tk
import tkinter.scrolledtext
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import Menu
from tkinter import PhotoImage
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import serial.tools.list_ports
import numpy as np
import webbrowser
import serial


class Interface:
    def __init__(self, master=None):
        self.fontePadrao = ("Calibri", "12")
        self.master = master
        # ----------------------------------------------------------------------------
        # Definição dos Containers e localização geométrica
        self.containerGeral = tk.Frame(self.master, highlightbackground="gray", highlightthickness=2)
        self.containerGeral.pack(expand=1,fill='both')
        # Estilos das fontes
        Style().configure("TButton", padding=4, relief="flat", font=('Calibri', 12))
        Style().configure("TLabel", font=('Calibri', 12))

        self.containerEsquerda = tk.Frame(self.containerGeral, width=550)
        self.containerEsquerda.pack_propagate(0)
        self.containerEsquerda.pack(side=tk.LEFT, fill='both')

        self.containerDireita = Frame(self.containerGeral)
        self.containerDireita.pack(side=tk.RIGHT, expand=1, fill='both')

        self.containerDTop = tk.Frame(self.containerDireita, highlightbackground="gray", highlightthickness=1)
        self.containerDTop.pack(expand=0, fill='both')

        self.containerDBot = Frame(self.containerDireita)
        self.containerDBot.pack(side=tk.BOTTOM)

        self.containerETop = tk.Frame(self.containerEsquerda, highlightbackground="gray", highlightthickness=1)
        self.containerETop.pack(side=tk.TOP, pady=15)

        self.containerEBot = Frame(self.containerEsquerda)
        self.containerEBot.pack(side=tk.BOTTOM,expand=1,fill='both')

        # Define o container que contém a comunicação
        self.comunicacao(self.containerETop)
        # ----------------------------------------------------------------------------
        self.parametros(self.containerDTop)
        # ----------------------------------------------------------------------------
        #self.notebook(self.containerEBot)
        self.terminal(self.containerDBot)
        self.grafico(self.containerEBot)
        # ----------------------------------------------------------------------------
        self.menu()
        # ----------------------------------------------------------------------------
        #self.botao1 = Button(self.containerDBot, text="Teste")
        #self.botao1['command'] = self.botao
        #self.botao1.pack()
        #self.ok = False
        # ----------------------------------------------------------------------------

    # ----------------------------------------------------------------------------
    # Cria o container da comunicação
    def comunicacao(self, container):

        self.esp = serial.Serial()
        self.espConectado = False
        self.soldando = False

        self.containerComunicacao = tk.Frame(container)
        self.containerComunicacao.pack(pady=10)

        self.containerConectar = Frame(self.containerComunicacao)
        self.containerConectar.grid(row=0, column=0, pady=2)


        self.ico = PhotoImage(file=r'Images/connect32.png')
        self.icoConectar = self.ico.subsample(2, 2)
        self.botaoConectar = Button(self.containerConectar, text='Conectar', image=self.icoConectar, compound=tk.LEFT)
        self.botaoConectar['command'] = self.botao_conectar
        self.botaoConectar['width'] = 10
        self.botaoConectar.grid(row=0, column=0, padx=(10, 10))

        self.ico = PhotoImage(file=r'Images/soldar32.png')
        self.icoSoldar = self.ico.subsample(2, 2)
        self.botaoSoldar = Button(self.containerConectar, text='Soldar', image=self.icoSoldar, compound=tk.LEFT)
        self.botaoSoldar['width'] = 10
        self.botaoSoldar['command'] = self.botao_soldar
        self.botaoSoldar.grid(row=0, column=1, padx=(10, 10))

        self.ico = PhotoImage(file=r'Images/abort32.png')
        self.icoAbortar = self.ico.subsample(2, 2)
        self.botaoAbortar = Button(self.containerConectar, text='Abortar', image=self.icoAbortar, compound=tk.LEFT)
        self.botaoAbortar['width'] = 10
        self.botaoAbortar.grid(row=0, column=2, padx=(10, 10))

        self.containerPorta = Frame(self.containerComunicacao)
        self.containerPorta.grid(row=1, column=0, pady=2)

        self.labelComs = Label(self.containerPorta, text='Porta')
        self.labelComs.grid(row=0, column=0, padx=(10, 2))

        self.comboComs = Combobox(self.containerPorta, width=30, state='readonly')
        self.atualizarComs()
        self.comboComs['values'] = self.listaComs
        self.comboComs.current(0)
        self.comboComs.grid(row=0, column=1, padx=(2, 10))

        self.botaoAtualizarComs = Button(self.containerPorta, text='Atualizar')
        self.botaoAtualizarComs['command'] = self.atualizarComs
        self.botaoAtualizarComs.grid(row=0, column=2, padx=(10, 10))

    # ----------------------------------------------------------------------------
    # Seleção dos parâmetros de solda
    def parametros(self, container):
        # Label e Combo box para definir o modo de Operação
        self.containerModo = Frame(container)
        self.containerModo.grid(row=0, column=0, pady=(10, 10))

        self.labelModo = Label(self.containerModo, text="Modo de Operação:")
        self.labelModo["font"] = self.fontePadrao
        self.labelModo.grid(row=0, column=0, padx=(10, 10))

        self.comboModo = Combobox(self.containerModo, width=20, state="readonly")
        itens = ("Constante", "Corrente Constante",
                 "Timer Constante", "Timer Corrente Constante")
        self.comboModo['values'] = itens
        self.comboModo.current(0)
        self.comboModo.grid(row=0, column=1, padx=(10, 10))

        # Label e Entry para frequência
        self.containerFreq = Frame(container)
        self.containerFreq.grid(row=1, column=0, pady=(10, 10))

        self.labelFreq = Label(self.containerFreq, text="Frequência:")
        self.labelFreq.focus()
        self.labelFreq["font"] = self.fontePadrao
        self.labelFreq.grid(row=0, column=0, padx=(10, 10))

        self.entryFreq = Entry(self.containerFreq, width=20)
        self.entryFreq.focus()
        self.entryFreq.grid(row=0, column=1, padx=(10, 10))

        self.containerDuty = Frame(container)
        self.containerDuty.grid(row=2, column=0, pady=(10, 10))

        self.labelDuty = Label(self.containerDuty, text= 'Duty Cycle:')
        self.labelDuty['font'] = self.fontePadrao
        self.labelDuty.grid(row=0, column=0, padx=(10, 10))

        self.entryDuty = Entry(self.containerDuty, width=20)
        self.entryDuty.grid(row=0, column=1, padx=(10, 10))

        self.containerCorrente = Frame(container)
        self.containerCorrente.grid(row=3, column=0, pady=(10, 10))

        self.labelCorrente = Label(self.containerCorrente, text='Corrente:')
        self.labelCorrente['font'] = self.fontePadrao
        self.labelCorrente.grid(row=0, column=0, padx=(10, 10))

        self.entryCorrente = Entry(self.containerCorrente, width=20)
        self.entryCorrente.grid(row=0, column=1, padx=(10, 10))

        self.containerTempo = Frame(container)
        self.containerTempo.grid(row=4, column=0, pady=(10, 10))

        self.labelTempo = Label(self.containerTempo, text='Tempo de Operação:')
        self.labelTempo.grid(row=0, column=0, padx=(10, 10))

        self.entryTempo = Entry(self.containerTempo, width=20)
        self.entryTempo.grid(row=0, column=1, padx=(10, 10))

    # ----------------------------------------------------------------------------
    # Cria o menu superior da interface
    def menu(self):
        # Menus da interface
        self.menu = Menu(self.master)

        self.menuSobre = Menu(self.menu, tearoff=0, activebackground='blue')
        self.menuSobre.add_command(label='Teste')
        self.menuSobre.add_command(label='Teste 2')
        self.menuSobre.add_separator()
        self.menuSobre.add_command(label='Sair', command=self.sair)

        self.menuAjuda = Menu(self.menu, tearoff=0, activebackground='blue')
        self.menuAjuda.add_command(label='Documentação', command=self.janelaAjuda)

        self.menu.add_cascade(label='Inicio', menu=self.menuSobre)

        self.menu.add_command(label='Sobre', command=self.janelaSobre)
        self.menu.add_cascade(label='Ajuda', menu=self.menuAjuda)

        self.master.config(menu=self.menu)

    # ----------------------------------------------------------------------------
    # Cria o gráfico do MatPlotLib
    def grafico(self, container):
        self.containerGrafico = tk.Frame(container,  highlightbackground="gray", highlightthickness=1)
        self.containerGrafico.pack(expand=1,fill='both')

        self.Fig = Figure(figsize=(5.4, 4.2), dpi=100)
        self.ax = self.Fig.add_subplot(111)

        self.ax.set_title("Corrente na Bobina")
        self.ax.set_xlabel("Tempo")
        self.ax.set_ylabel("Corrente [A]")
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(-0.2, 25)
        self.lines = self.ax.plot([], [])[0]
        self.data = np.array([])

        self.canvas = FigureCanvasTkAgg(self.Fig, self.containerGrafico)
        self.canvas.get_tk_widget().pack(pady=10)
        self.canvas.draw()

    # ----------------------------------------------------------------------------
    # Terminal para comunicar com a fonte
    def terminal(self, container):

        self.containerTerminal = Frame(container)
        self.containerTerminal.pack(expand=0, fill='none')

        self.texto = tkinter.scrolledtext.ScrolledText(self.containerTerminal, width=50, height=20)
        self.texto.configure(state='disabled')
        self.texto.pack(expand=1, fill='y')

        self.containerTerminalEntry = Frame(container)
        self.containerTerminalEntry.pack(side=tk.BOTTOM, expand=1, fill='x')

        self.comandoSerial = tk.StringVar()

        self.entryTerminal = Entry(self.containerTerminalEntry, width=40, textvariable=self.comandoSerial)
        self.entryTerminal.pack(side=tk.LEFT, padx=10)

        self.botaoEnviar = Button(self.containerTerminalEntry, text='Enviar')
        self.botaoEnviar['command'] = self.botao_enviarSerial
        self.botaoEnviar.configure(padding=0)
        self.botaoEnviar.pack(side=tk.RIGHT, padx=10, pady=5)
    # ----------------------------------------------------------------------------
    # Cria o Widget Notebook que contem o gráfico e o terminal
    def notebook(self, container):
        self.tab_control = Notebook(container)
        self.tab1 = Frame(self.tab_control)
        self.tab2 = Frame(self.tab_control)

        self.tab_control.add(self.tab1, text='Corrente')
        self.grafico(self.tab1)

        self.tab_control.add(self.tab2, text='Terminal')
        self.terminal(self.tab2)
        self.tab_control.pack(expand=1,fill='both')
    # ----------------------------------------------------------------------------
    # Atualiza a lista de portas Seriais disponíveis no sistema
    def atualizarComs(self):
        ports = serial.tools.list_ports.comports()
        self.listaComs = []
        for port, desc, hwid in sorted(ports):
            self.listaComs.append(port)
        if len(self.listaComs) == 0:
            self.listaComs.append(' ')
        self.comboComs['values'] = self.listaComs
        self.comboComs.current(0)

    # ----------------------------------------------------------------------------
    # Janela que mostra as informações sobre o Autor
    def janelaSobre(self):
        msg = "Nome: Matheus Vinícius Resende Nascimento\n" \
              "Estudante de Engenharia Elétrica na FEG-UNESP\n" \
              "Bolsista CNPQ\n" \
              "Versão 1.0 - Julho de 2021\n" \
              r"https:\\www.google.com.br"  # Link do GitHub do projeto.
        messagebox.showinfo('Sobre o autor', msg)

    # ----------------------------------------------------------------------------
    # Janela que redireciona para a documentação da fonte
    def janelaAjuda(self):
        link = 'https://github.com/'  # Link da documentação no GitHub
        webbrowser.open(link, new=2)

    # ----------------------------------------------------------------------------
    # Função para sair
    def sair(self):
        self.master.quit()
        self.master.destroy()

    # ----------------------------------------------------------------------------
    # Método para atualizar o gráfico
    def plotData(self, corrente):

        #if self.ok:
            #a = np.random.randint(20)

        if (len(self.data) < 100):
            self.data = np.append(self.data, corrente)
        else:
            self.data[0:99] = self.data[1:100]
            self.data[99] = corrente

        self.lines.set_xdata(np.arange(0, len(self.data)))
        self.lines.set_ydata(self.data)

        self.canvas.draw()

    # ----------------------------------------------------------------------------

    def msgErro(self, msg):
        messagebox.showinfo('Erro', msg)

    def botao_conectar(self):
        if not self.espConectado:
            self.esp.port = self.comboComs.get()
            self.esp.baudrate = 115200
            self.esp.timeout = 0.5
            try:
                self.esp.open()
            except Exception:
                self.msgErro('Impossível conectar!\nPorta COM não encontrada')
            if(self.esp.is_open):
                self.botaoConectar['text'] = 'Desconectar'
                self.espConectado = True
        else:
            self.esp.close()
            self.botaoConectar['text'] = 'Conectar'
            self.espConectado = False

    def botao_enviarSerial(self):
        if(self.esp.is_open):
            comando = self.comandoSerial.get()
            if comando != '':
                self.texto.configure(state='normal')
                self.texto.insert(tk.INSERT, comando + '\n')
                self.texto.configure(state='disabled')
                self.comandoSerial.set('')
                self.entryTerminal.focus_set()
                self.enviarSerial(comando)
        else:
            self.msgErro('Soldadora não está conectada')

    def enviarSerial(self, msg):
        try:
            self.esp.write(bytes(msg, 'utf-8'))
        except:
            self.msgErro('Soldadora não conectada')

    def lerSerial(self):
        if(self.esp.is_open):
            if(self.esp.in_waiting > 0):
                self.changeTerminal(self.esp.read_until().decode('utf-8','ignore'))

        self.master.after(10, self.lerSerial)

    def changeTerminal(self, msg):
        self.texto.configure(state='normal')
        self.texto.insert(tk.INSERT, msg)
        self.texto.configure(state='disabled')
        if (msg[:4] == 'Recv'):
            if(msg[5] == 'C'):
                C = float(msg[6:msg.index('\r')])
                C = (C/1000) * 15
                self.plotData(C)

    def botao_soldar(self):
        if(not self.espConectado):
            self.msgErro("A soldadora não está conectada!")
        else:
            if(not self.soldando):
                self.botaoSoldar.configure(**self.botaoAtivado)
                self.enviarSerial("CE 1")
                self.soldando = True
            else:
                self.botaoSoldar['fg'] = 'gray'
                self.enviarSerial("CE 0")
                self.soldando = False