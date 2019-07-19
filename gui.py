import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import cv2
import numpy as np
import time, os, glob, json, re, ast, io
from PIL import Image, ImageTk
import pytesseract as tesseract

import func

LARGE_FONT = ("Helvetica", 12)
DISPLAY_FONT = ("Helvetica", 16)


# VARIAVEIS GLOBAIS
path = ""
bdPath = ""
materia = ""
assunto = ""
sigla = ""

materias = {
'biologia':['bioquimica','botanica','citologia','ecologia','embriologia',
'evolucao','fisiologiaHumana','genetica','imunologia','microbiologia',
'zoologiaParasitologia'],
'espanhol':[''],
'filosofiaESociologia':[],
'fisica':['cinematica','dinamica','eletrodinamica','eletromagnetismo',
'eletrostatica','estaticaHidrostatica','moderna','ondulatoria',
'optica','termodinamica'],
'geografia':['biogeografia','cartografia','climatologia','demografia',
'energia','geografiaAgraria','geografiaBrasil','geografiaCultural',
'geografiaEconomica','geografiaEconomicaBrasil','geografiaRegional',
'geografiaUrbana','geologia','geomorfologia','geopolitica','hidrologia',
'impactosAmbientais'],
'historia':['historiaAfrica','historiaAmerica','historiaAntiga','historiaAsia',
'historiaBrasil','historiaContemporanea','historiaMedieval','historiaModerna',
'preHistoria'],
"ingles":[],
'matematica':['analiseCombinatoriaProbabilidade','conjuntosNumericos','estatistica',
'funcoes','geometriaAnalitica','geometriaEspacial','geometriaPlana','matrizesSistemas',
'polinomio','progresso','razaoPropocao','trigonometria'],
'portugues':['gramatica', 'interpretacao','literatura'],
'quimica':['cineticaQuimica','densidade','equilibrioQuimico','estequiometria',
'gases','ligacaoQuimica','materiais','organica','oxirreducao','radioatividade',
'reacaoInorganica','separacaoMisturas','solucao','tabelaPeriodica','termoquimica']}

vests = ["enem", "fuve", "unic", "unes", "ufsc", "uffu",
        "mack", "puuc", "feei"]

# GUI
class extrairQuestaoApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        # COMEÇANDO COM TELA MAXIMIZADA
        # w, h = tk.Tk.winfo_screenwidth(self), tk.Tk.winfo_screenheight(self)
        # tk.Tk.geometry(self, "%dx%d+0+0" % (w, h))
        # NAO FUNCIONA NO UBUNTU
        tk.Tk.minsize(self, width=1280, height=720)
        tk.Tk.state(self,'zoomed')
        tk.Tk.iconbitmap(self,default='appEducacao_ferramenta.ico')
        tk.Tk.wm_title(self, "AppEducacao - Extrair Questão")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # for F in (StarPage, Main):

        frame = Main(container, self)
        self.frames[Main] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        # PRIMEIRA PÁGINA A APARECER STARTPAGE
        self.show_frame(Main)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()


class Main(tk.Frame):

    def __init__(self, parent, controller):
        self.frame = tk.Frame.__init__(self, parent)

        ## VARIAVEIS
        self.cur = 0 # IMAGEM ATUAL
        self.total = 0 # TOTAL DE IMAGENS
        self.imgs = [] # CAMINHOS DAS IMAGENS
        self.STATE = {} # ESTADO DO MOUSE
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0,0
        self.rec = None # RETÂNGULOS DESENHADOS
        self.recList = [] # RETÂNGULOS DESENHADOS
        self.recImgEnun = [] # LISTA DOS DADOS RETANGULOS IMG ENUN
        self.recImgAlt = [] # LISTA DOS DADOS RETANGULOS IMG ALT
        self.recAlt = [] # LISTA DOS DADOS RETANGULOS ALT
        self.clickImgEnun = 0 # INDICAR CLIQUE NA FERRAMENTA IMG ENUN
        self.clickImgAlt = 0 # INDICAR CLIQUE NA FERRAMENTA IMG ALT
        self.clickAlt = 0 # INDICAR CLIQUE NA FERRAMENTA ALT
        self.imgReal = None # IMAGEM REAL LIDA DA PASTA
        self.imgShow = None # IMAGEM REDIMENSIONADA
        self.imgsRecortadas = [] # IMAGENS RECORTADAS
                

        ## GUI
        # SELECIONAR PASTA
        ttk.Label(self, text="Pasta", font=LARGE_FONT).place(relx=0.01, rely=0.02)
        self.pastaTxt = ttk.Entry(self, state="readonly")
        self.pastaTxt.bind('<Button-1>', self.selPasta)
        self.pastaTxt.place(relx=0.05,rely=0.02, relwidth=0.53)

        # DIGITAR MATERIA
        ttk.Label(self, text="Matéria",
                font=LARGE_FONT, wraplength = 200).place(relx=0.01, rely=0.05)
        self.materiaCmb = ttk.Combobox(self,values=list(materias.keys()), state='readonly')
        self.materiaCmb.bind('<<ComboboxSelected>>', self.atualizaCmb)
        self.materiaCmb.place(relx=0.05, rely=0.05, relwidth=0.12)

        # DIGITAR ASSUNTO
        ttk.Label(self, text="Assunto",
                font=LARGE_FONT, wraplength = 200).place(relx=0.18, rely=0.05)
        self.assuntoCmb = ttk.Combobox(self, state='readonly')
        self.assuntoCmb.place(relx=0.22, rely=0.05, relwidth=0.15)

        # DIGITAR SIGLA
        ttk.Label(self, text="Vestibular",
                font=LARGE_FONT, wraplength = 200).place(relx=0.38, rely=0.05)
        self.siglaCmb = ttk.Combobox(self, values=vests, state='readonly')
        self.siglaCmb.place(relx=0.43, rely=0.05, relwidth=0.15)

        # DIGITAR NÚMERO DA QUESTÃO
        ttk.Label(self, text="Número da Questão",
                font=LARGE_FONT, wraplength = 200).place(relx=0.68, rely=0.02)
        self.questaoTxt = ttk.Entry(self)
        self.questaoTxt.insert(tk.INSERT,"1")
        self.questaoTxt.place(relx=0.78,rely=0.02, width=75)

        # LABELS
        ttk.Label(self, text="Questão", font=LARGE_FONT).place(relx=0.01, rely=0.12)
        ttk.Label(self, text="JSON", font=LARGE_FONT).place(relx=0.62, rely=0.12)
        ttk.Label(self, text="Ferramentas", font=LARGE_FONT).place(relx=0.52, rely=0.12)
        ttk.Label(self, text="BBox", font=LARGE_FONT).place(relx=0.52, rely=0.25)

        # BOTÕES
        self.carregarBtn = ttk.Button(self, text="Carregar",
                                        command=lambda: self.loadingImages(self.siglaCmb.get(),
                                        self.assuntoCmb.get(),self.materiaCmb.get()))
        self.carregarBtn.place(relx=0.60,rely=0.02, width=100,height=50)

        self.excluirBtn = ttk.Button(self, text="Excluir")
        self.excluirBtn.bind("<Button-1>", self.excluiRec)
        self.excluirBtn.place(relx=0.52,rely=0.68,relwidth=0.09)

        self.excluirAllBtn = ttk.Button(self, text="Excluir Todos")
        self.excluirAllBtn.bind("<Button-1>", self.excluiTodosRec)
        self.excluirAllBtn.place(relx=0.52,rely=0.71,relwidth=0.09)

        self.gerarBtn = ttk.Button(self, text="Gerar JSON")
        self.gerarBtn.bind("<Button-1>", self.gerJson)
        self.gerarBtn.place(relx=0.52,rely=0.74,relwidth=0.09)

        self.salvarBtn = ttk.Button(self, text="Salvar")
        self.salvarBtn.bind("<Button-1>", self.salvarAll)
        self.salvarBtn.place(relx=0.92,rely=0.02)

        self.cancelarBtn = ttk.Button(self, text="Cancelar")
        self.cancelarBtn.bind("<Button-1>", self.cancelAll)
        self.cancelarBtn.place(relx=0.92,rely=0.05)

        self.anteriorBtn = ttk.Button(self, text="<< Anterior", command=lambda: self.antImg())
        self.anteriorBtn.place(relx=0.06,rely=0.12)

        self.proximoBtn = ttk.Button(self, text="Próximo >>",command=lambda: self.proxImg())
        self.proximoBtn.place(relx=0.11,rely=0.12)

        # BOTÕES FUNÇÕES
        self.enuImgBtn = tk.Button(self, text="Imagem Enunciado", foreground='red')
        self.enuImgBtn.bind("<Button-1>", self.imgEnun)
        self.enuImgBtn.place(relx=0.52,rely=0.15,relwidth=0.09)

        self.altImgBtn = tk.Button(self, text="Imagem Alternativa", foreground='green')
        self.altImgBtn.bind("<Button-1>", self.imgAlt)
        self.altImgBtn.place(relx=0.52,rely=0.185,relwidth=0.09)

        self.altBtn = tk.Button(self, text="Alternativa", foreground='blue')
        self.altBtn.bind("<Button-1>", self.alt)
        self.altBtn.place(relx=0.52,rely=0.22,relwidth=0.09)

        # CANVAS
        self.imgCv = tk.Canvas(self, background="white", cursor='tcross')
        # self.imgCv.place(relx=0.01,rely=0.15,relwidth=0.5,relheight=0.80)
        self.imgCv.bind("<Button-1>", self.mouseClick) # Ao clicar
        self.imgCv.bind("<Motion>", self.mouseMove) # Ao mexer o mouse
        self.imgCv.bind("<Escape>", self.cancelRec) # Ao apertar esc
        self.imgCv.place(relx=0.01,rely=0.15)

        # LISTBOX
        self.bbLst = tk.Listbox(self)
        self.bbLst.place(relx=0.52,rely=0.27,relwidth=0.09, relheight=0.4)

        # TEXTBOX
        self.jsonTxt = tk.Text(self,width=200,height=400,background="white", foreground="black")
        self.jsonTxt.config(state="normal")
        self.jsonTxt.place(relx=0.62,rely=0.15,relwidth=0.36,relheight=0.80)

        # CRIAR PASTA TEMPORÁRIA
        self.pastaTemp()

        # VARIÁVEIS
        self.FLAG_SALVAR = 0 # QUANTAS VEZES O BOTÃO DE SALVAR FOI APERTADO
        self.FLAG_VER = int(self.questaoTxt.get()) # NÚMERO DO WIDGET NUM QUESTAO
    
    ## FUNÇÕES
    def mouseClick(self, event):
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y

        if (self.STATE['click'] != 0) and (self.clickImgEnun == 1):
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            x1, y1, x2, y2 = self.converteCoord(x1, y1, x2, y2)
            self.recImgEnun.append((x1, y1, x2, y2))
            self.recList.append(self.rec)
            self.rec = None
            self.bbLst.insert(tk.END,'(%d,%d) -> (%d, %d)' % (x1,y1,x2,y2))
            self.bbLst.itemconfig(len(self.recList)-1, fg='red')
            # self.clickImgEnun = 0

        if (self.STATE['click'] != 0) and (self.clickImgAlt == 1):
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            x1, y1, x2, y2 = self.converteCoord(x1, y1, x2, y2)
            self.recImgAlt.append((x1, y1, x2, y2))
            self.recList.append(self.rec)
            self.rec = None
            self.bbLst.insert(tk.END,'(%d,%d) -> (%d, %d)' % (x1,y1,x2,y2))
            self.bbLst.itemconfig(len(self.recList)-1, fg='green')
            # self.clickImgAlt = 0

        if (self.STATE['click'] != 0) and (self.clickAlt == 1):
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            x1, y1, x2, y2 = self.converteCoord(x1, y1, x2, y2)
            self.recAlt.append((x1, y1, x2, y2))
            self.recList.append(self.rec)
            self.rec = None
            self.bbLst.insert(tk.END,'(%d,%d) -> (%d, %d)' % (x1,y1,x2,y2))
            self.bbLst.itemconfig(len(self.recList)-1, fg='blue')
            # self.clickAlt = 0

        self.STATE['click'] = 1 - self.STATE['click']
        self.imgCv.focus_set()

    def mouseMove(self, event):
        if (self.STATE['click'] == 1) and (self.clickImgEnun == 1):
            if self.rec:
                self.imgCv.delete(self.rec) # NÃO FICAR RASTRO
            self.rec = self.imgCv.create_rectangle(self.STATE['x'],self.STATE['y'], event.x, event.y, width=2, outline='red')

        if (self.STATE['click'] == 1) and (self.clickImgAlt == 1):
            if self.rec:
                self.imgCv.delete(self.rec) # NÃO FICAR RASTRO
            self.rec = self.imgCv.create_rectangle(self.STATE['x'],self.STATE['y'], event.x, event.y, width=2, outline='green')
        
        if (self.STATE['click'] == 1) and (self.clickAlt == 1):
            if self.rec:
                self.imgCv.delete(self.rec) # NÃO FICAR RASTRO
            self.rec = self.imgCv.create_rectangle(self.STATE['x'],self.STATE['y'], event.x, event.y, width=2, outline='blue')
    
    # FUNCAO QND SELECIONA FERRAMENTA IMAGEM ENUNCIADO 
    def imgEnun(self, event):
        self.clickImgEnun = 1
        self.clickAlt = 0
        self.clickImgAlt = 0
        self.cancelRec(event)

    # FUNCAO QND SELECIONA FERRAMENTA IMAGEM ALTERNATIVA
    def imgAlt(self, event):
        self.clickImgAlt = 1
        self.clickImgEnun = 0
        self.clickAlt = 0
        self.cancelRec(event)

    # FUNCAO QND SELECIONA FERRAMENTA ALTERNATIVA
    def alt(self, event):
        self.clickAlt = 1
        self.clickImgAlt = 0
        self.clickImgEnun = 0
        self.cancelRec(event)

    def cancelRec(self, event):
        if self.STATE['click'] == 1:
            if self.rec:
                self.imgCv.delete(self.rec)
                self.rec = None
            self.STATE['click'] = 0 

    # FUNCAO QND QUER EXCLUIR TODOS OS RETANGULOS
    def excluiTodosRec(self, event=None):
        for idx in range(len(self.recList)):
            self.imgCv.delete(self.recList[idx])
        self.bbLst.delete(0,len(self.recList))
        self.recList = []
        self.recAlt = []
        self.recImgAlt = []
        self.recImgEnun = []

    def excluiRec(self, event):
        auxRed = []
        auxGreen = []
        auxBlue = []
        i = 0
        item = self.bbLst.curselection()
        if len(item) != 1:
            return # SELECIONOU MAIS DE UM ITEM
        # FAZER UMA LISTA DE TODOS OS ITENS PRESENTES NA LISTBOX
        # TEM QUE CONTER FG E INDEX
        for i in range(len(self.recList)):
            if self.bbLst.itemcget(i,"foreground") == "red":
                auxRed.append(i)
            if self.bbLst.itemcget(i,"foreground") == "green":
                auxGreen.append(i)
            if self.bbLst.itemcget(i,"foreground") == "blue":
                auxBlue.append(i)
        
        idx = int(item[0])
        fgItem = self.bbLst.itemcget(idx,"foreground")
        self.imgCv.delete(self.recList[idx])
        self.bbLst.delete(idx)
        self.recList.pop(idx)
        if fgItem == "red":
            for i in range(len(auxRed)):
                if idx == auxRed[i]:
                    self.recImgEnun.pop(i)

        if fgItem == "green":
            for i in range(len(auxGreen)):
                if idx == auxGreen[i]:
                    self.recImgAlt.pop(i)

        if fgItem == "blue":
            for i in range(len(auxBlue)):
                if idx == auxBlue[i]:
                    self.recAlt.pop(i)

    # CARREGA TODAS AS IMAGENS
    def loadingImages(self,mat,ass,sig):
        global path,materia,assunto,sigla
        materia = mat
        assunto = ass
        sigla = sig

        print("LOADING IMAGES")
        for f in func.extra.orgLista(glob.glob(path+"/"+"*.png")):
            self.imgs.append(f)
        print("LOADING IMAGES SUCESS!")
        self.cur =0
        self.tkimg = self.readingImg(self.imgs[self.cur])
        self.showImg(self.tkimg)

    def readingImg(self, imgPath):
        w_sis = tk.Frame.winfo_screenwidth(self)
        h_sis = tk.Frame.winfo_screenheight(self)
        w_canva = int(0.49*w_sis)
        h_canva = int(0.8*h_sis)
        img = Image.open(imgPath)
        self.imgReal = img
        w, h = img.size
        if (w > w_canva) or (h > h_canva):
            ratio = w/h
            if (w > w_canva) and (h < h_canva):
                img = img.resize((int(ratio*h),h))
            if (h > h_canva) and (w < w_canva):
                img = img.resize((w,int(w/ratio)))
            if (w > w_canva) and (h > h_canva):
                if (w > h):
                    img = img.resize((w_canva,int(w_canva/ratio)))
                if (h > w):
                    img = img.resize((int(h_canva*ratio),h_canva))
                if (h == w):
                    img = img.resize((int(h_canva*ratio),h_canva))
            self.imgShow = img
            storeobj = ImageTk.PhotoImage(img)
        else:
            self.imgShow = img
            storeobj = ImageTk.PhotoImage(img)
        return storeobj

    def showImg(self, obj):
        self.imgCv.config(width = obj.width(), 
        height = obj.height())
        self.imgCv.create_image(0, 0, image = obj, anchor='nw')
        self.imgCv.update()
    
    def proxImg(self):
        print("PRÓXIMA IMAGEM")
        self.cur += 1
        self.tkimg = self.readingImg(self.imgs[self.cur])
        self.showImg(self.tkimg)
        self.excluiTodosRec()
        self.jsonTxt.delete('1.0', tk.END)
    
    def antImg(self):
        print("ANTERIOR IMAGEM")
        self.cur -= 1
        self.tkimg = self.readingImg(self.imgs[self.cur])
        self.showImg(self.tkimg)
        self.excluiTodosRec()
        self.jsonTxt.delete('1.0', tk.END)
    
    def selPasta(self, event):
        file_path = filedialog.askdirectory(title = "Escolha uma pasta")
        global path
        path = file_path
        self.pastaTxt.configure(state="")
        self.pastaTxt.delete(0,"end")
        self.pastaTxt.insert(0,file_path)
        self.pastaTxt.configure(state="readonly")
                
    def atualizaCmb(self, event):
        self.assuntoCmb['values'] = materias[self.materiaCmb.get()]

    def converteCoord(self, x1, y1, x2, y2):
        w_real, h_real = self.imgReal.size
        w_redim, h_redim = self.imgShow.size

        x_var = w_real/w_redim
        y_var = h_real/h_redim

        xout1 = x_var*x1
        xout2 = x_var*x2
        yout1 = y_var*y1
        yout2 = y_var*y2

        return [xout1, yout1, xout2, yout2]
    
    def gerJson(self, event):

        # INICIANDO LÓGICA
        inicio = time.time()
        self.nomeImgSave = []
        self.imgsRecortadas = self.recorteCanvas()
        sigla = self.siglaCmb.get()
        data = {}
        text = None
        # PEGAR NUMERO DA QUESTAO DO ENTTRY TEXT
        aux = int(self.questaoTxt.get())
        if (self.FLAG_VER == aux):
            aux = aux + self.FLAG_SALVAR
        else:
            aux = aux
            self.FLAG_VER = aux
            self.FLAG_SALVAR = 0

        u = 1
        for img in self.imgsRecortadas:
            image, tag = img
            print(tag)
            if tag == "enun":
                name = str(u) +"_"+ "enun"
                imgTreat = self.prepareImage(image)
                text = self.lerImg(imgTreat)
                data[str(name)] = text
                u += 1

            if tag == "alt":
                name = str(u) +"_"+ "alt"
                imgTreat = self.prepareImage(image)
                text = self.lerImg(imgTreat)
                listAlt = []
                listAlt.append(text)
                data[str(name)] = "[" + text + "]"
                # data[str(name)] = str(listAlt)
                u += 1

            if tag == "imgAlt":
                nImg = sigla + "_" + str(aux) + "_" + str(u) + ".png"
                name = str(u) + "_"+ "imgAlt"
                self.nomeImgSave.append(nImg)
                data[name] = nImg
                u += 1

            if tag == "imgEnun":
                nImg = sigla + "_" + str(aux) + "_" + str(u) + ".png"
                name = str(u) + "_"+ "imgEnun"
                data[name] = nImg
                self.nomeImgSave.append(nImg)
                u += 1

        data["Gabarito"] = ""

        self.displayJson(data)

        fim = time.time()
        tempo = fim-inicio
        print("Tempo de leitura demorou: ", tempo)


    
    def displayJson(self, data):

        self.jsonTxt.config(font=DISPLAY_FONT)
        self.jsonTxt.config(spacing2=7)
        self.jsonTxt.delete(1.0,tk.END)
        # self.jsonTxt.insert(tk.END, data)

        self.jsonTxt.insert(tk.END, "{\n\n")
        for key in data:
            
            self.jsonTxt.insert(tk.END, "\""+key+"\": ")
            self.jsonTxt.insert(tk.END, "\""+data[key]+"\",")
            self.jsonTxt.insert(tk.END, "\n\n")
        
        self.jsonTxt.insert(tk.END, "}")

    def salvarAll(self, event):

        inicio = time.time()
        actualPath = os.getcwd()
        pathTemp = actualPath + "/temp/"
        aux = int(self.questaoTxt.get())
        if (self.FLAG_VER == aux):
            aux = aux + self.FLAG_SALVAR
        else:
            aux = aux
            self.FLAG_VER = aux
            self.FLAG_SALVAR = 0
        sigla = self.siglaCmb.get()
        u = 0
        # ast.literal_eval transforma string em dicionário
        data = ast.literal_eval(self.jsonTxt.get(1.0, tk.END)) # LE TUDO DO TXTBOX
        # ADICIONANDO AO DATA
        data["Acertos"] = 0
        data["Erros"] = 0
        data["Ranking"] = "" 

        with io.open(pathTemp + sigla+"_"+str(aux)+".JSON", 'w', encoding='utf8') as outfile:
            print("Salvando o json")
            json_data = json.dump(data, outfile, sort_keys=True, indent=3, ensure_ascii=False)
        
        for img in self.imgsRecortadas:
            image, tag = img
            print(tag)
            if tag == "imgAlt":
                nImg = self.nomeImgSave[u]
                nImg = pathTemp + nImg
                image.save(nImg, 'PNG')
                u += 1

            if tag == "imgEnun":
                nImg = self.nomeImgSave[u]
                nImg = pathTemp + nImg
                image.save(nImg, 'PNG')
                u += 1

        
        self.FLAG_SALVAR += 1
        self.proxImg()
        fim = time.time()
        tempo = fim - inicio
        print("Salvar tudo demorou: ", tempo)
    
    def pastaTemp(self):
        try:
            # IDENTIFICA EM QUE PASTA ESTAMOS
            actualPath = os.getcwd()
            # CRIA PASTA TEMP NO DIRETÓRIO ATUAL
            os.mkdir(actualPath+"/temp")
        except Exception as e:
            print(e)

    def cancelAll(self,event):
        self.excluiTodosRec()
        self.jsonTxt.delete('1.0', tk.END)
        

    def prepareImage(self, pillowImg):
        # CONVERTER PARA UM OBJETO OPENCV
        img = cv2.cvtColor(np.array(pillowImg), cv2.COLOR_RGB2BGR)
        # FILTRO
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        kernel = np.ones((1, 1), np.uint8)
        img = cv2.dilate(img, kernel, iterations=1)
        img = cv2.erode(img, kernel, iterations=1)
        img = cv2.adaptiveThreshold(
                                    cv2.bilateralFilter(img, 9, 75, 75),
                                    255,
                                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY,
                                    31,
                                    2)
        return img
    
    def lerImg(self, pillowImg):
        imgTreat = self.prepareImage(pillowImg)
        text = tesseract.image_to_string(imgTreat, lang='por+equ', config='--psm 6')
        modified = re.sub(r"(\\n)"," ", repr(text))

        return modified


    def recorteCanvas(self):
        self.imgsTag = []
    # CASO 1
        # QUESTAO NÃO TEM IMAGENS E ALTERNATIVAS NÃO TEM IMAGENS 
        if (len(self.recAlt) == 1) and (len(self.recImgAlt) == 0) and (len(self.recImgEnun) == 0):
            u = 1
            crop = None
            x1, y1, x2, y2 = self.recAlt[0]
            w, h = self.imgReal.size
            crop = self.imgReal.crop((0, 0, w, y1))
            # crop.save(str(u)+'_enun'+'.png', 'PNG')
            self.imgsTag.append([crop,"enun"])
            u += 1
            crop = self.imgReal.crop((x1, y1, x2, y2))
            # crop.save(str(u)+'_alt'+'.png', 'PNG')
            self.imgsTag.append([crop,"alt"])

    # CASO 2
        # QUESTÃO TEM IMAGEM NO ENUNCIADO E ALTERNATIVA NORMAL
        elif (len(self.recAlt) == 1) and (len(self.recImgEnun) > 0) and (len(self.recImgAlt) == 0):
            self.recImgEnun.sort(key=lambda x: x[1])
            u = 1
            crop = None
            x1, y1, x2, y2 = self.recImgEnun[0]
            w, h = self.imgReal.size
            crop = self.imgReal.crop((0,0, w, y1))
            # crop.save(str(u)+'_enun'+'.png', 'PNG')
            self.imgsTag.append([crop,"enun"])
            u += 1
            for i in range(len(self.recImgEnun)):
                x1, y1, x2, y2 = self.recImgEnun[i]
                crop = self.imgReal.crop((x1,y1, x2, y2))
                # crop.save(str(u)+'_imgEnun'+'.png', 'PNG')
                self.imgsTag.append([crop,"imgEnun"])
                u += 1
                if i < (len(self.recImgEnun) - 1):
                    x1_,y1_,x2_,y2_ = self.recImgEnun[i+1]
                    crop = self.imgReal.crop((0,y2, w, y1_))
                    # crop.save(str(u)+'_enun'+'.png', 'PNG')
                    self.imgsTag.append([crop,"enun"])
                    u += 1
            
            x1_, y1_, x2_, y2_ = self.recAlt[0]
            crop = self.imgReal.crop((0,y2, w, y1_))
            # crop.save(str(u)+'_enun'+'.png', 'PNG')
            self.imgsTag.append([crop,"enun"])
            u += 1
            crop = self.imgReal.crop((x1_,y1_, x2_, y2_))
            # crop.save(str(u)+'_alt'+'.png', 'PNG')
            self.imgsTag.append([crop,"alt"])
    
    # CASO 3
        # QUESTÃO NÃO TEM IMAGENS ENUNCIADO SÓ HÁ IMAGENS NAS ALTERNATIVAS
        elif (len(self.recAlt) == 0) and (len(self.recImgEnun) == 0) and (len(self.recImgAlt) > 0):
            self.recImgAlt.sort(key=lambda x: x[1]) # ORDENA CRESCENTE Y1
            u = 1
            crop = None
            x1, y1, x2, y2 = self.recImgAlt[0]
            w, h = self.imgReal.size
            crop = self.imgReal.crop((0,0, w, y1))
            # crop.save(str(u)+'_enun'+'.png', 'PNG')
            self.imgsTag.append([crop,"enun"])
            u += 1
            for i in range(len(self.recImgAlt)):
                x1, y1, x2, y2 = self.recImgAlt[i]
                crop = self.imgReal.crop((x1,y1, x2, y2))
                # crop.save(str(u)+'_imgAlt'+'.png', 'PNG')
                self.imgsTag.append([crop,"imgAlt"])
                u += 1
    
    # CASO 4
        # QUESTÃO TEM IMAGEM NO ENUNCIADO E IMAGEM NAS ALTERNATIVAS
        elif (len(self.recAlt) == 0) and (len(self.recImgEnun) > 0) and (len(self.recImgAlt) > 0):
            self.recImgEnun.sort(key=lambda x: x[1])
            self.recImgAlt.sort(key=lambda x: x[1])
            u = 1
            crop = None
            x1, y1, x2, y2 = self.recImgEnun[0]
            w, h = self.imgReal.size
            crop = self.imgReal.crop((0,0, w, y1))
            # crop.save(str(u)+'_enun'+'.png', 'PNG')
            self.imgsTag.append([crop,"enun"])
            u += 1
            for i in range(len(self.recImgEnun)):
                x1, y1, x2, y2 = self.recImgEnun[i]
                crop = self.imgReal.crop((x1,y1, x2, y2))
                # crop.save(str(u)+'_imgEnun'+'.png', 'PNG')
                self.imgsTag.append([crop,"enun"])
                u += 1
                if i < (len(self.recImgEnun) - 1):
                    x1_,y1_,x2_,y2_ = self.recImgEnun[i+1]
                    crop = self.imgReal.crop((0,y2, w, y1_))
                    # crop.save(str(u)+'_enun'+'.png', 'PNG')
                    self.imgsTag.append([crop,"enun"])
                    u += 1
            
            x1_, y1_, x2_, y2_ = self.recImgAlt[0]
            crop = self.imgReal.crop((0,y2, w, y1_))
            crop.save(str(u)+'_enun'+'.png', 'PNG')
            self.imgsTag.append([crop,"enun"])
            u += 1
            for i in range(len(self.recImgAlt)):
                x1, y1, x2, y2 = self.recImgAlt[i]
                crop = self.imgReal.crop((x1,y1, x2, y2))
                # crop.save(str(u)+'_imgAlt'+'.png', 'PNG')
                self.imgsTag.append([crop,"imgAlt"])
                u += 1

        # CASO NÃO SEJA NENHUM DOS CASOS ACIMA MOSTRAR A MENSAGEM
        else:
            messagebox.showinfo("Erro!", "Algo de errado aconteceu. Veja se você não desenhou na mesma imagem com as ferramentas de Imagem Alternativa e Alternativa, cores verdes e azul respectivamente. Lembrando que só pode conter uma delas.")
        # print(self.imgsTag)
        return self.imgsTag

        
app = extrairQuestaoApp()
app.mainloop()