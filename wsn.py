import matplotlib.pyplot as plt
import matplotlib
import tkinter
from tkinter import ttk
import numpy as np

matplotlib.use('TkAgg')

#class définissant les composants(microprocesseur,capteurs...) avec les differents temps et puissances
class composant:
    def __init__(self,p_veille,t_reveil,p_reveil,t_actif,p_actif):
        self.p_veille = p_veille
        self.t_reveil = t_reveil
        self.p_reveil = p_reveil
        self.t_actif = t_actif
        self.p_actif = p_actif
    
    def __str__(self):
        return "p_veille: " + str(self.p_veille) + " t_reveil: " + str(self.t_reveil) + " p_reveil: " + str(self.p_reveil) + " t_actif: " + str(self.t_actif) + " p_actif: " + str(self.p_actif)

#class définissant le composant batterie
class Baterie:
    def __init__(self,charge_initial,puissance_recharge):
        self.charge_initial = charge_initial
        self.puissance_recharge = puissance_recharge 

#Calcul d'énergie necessaire aux differentes étapes du cycle
def EnergieReveilMicrocontroleur(composants,capteurs):
    energie = composants[0].p_reveil*composants[0].t_reveil
    energie += composants[1].p_veille*composants[0].t_reveil
    for capteur in capteurs:
        energie += capteur.p_veille*composants[0].t_reveil
    return energie

def EnergieReveilCapteurs(composants,capteurs):
    higherTime = 0
    for capteur in capteurs:
        if capteur.t_reveil > higherTime:
            higherTime = capteur.t_reveil

    energie = composants[0].p_actif*higherTime

    for capteur in capteurs:
        energie += capteur.p_reveil*higherTime

    energie += composants[1].p_veille*higherTime
    return energie

def EnergieMesures(composants,capteurs):
    higherTime = 0
    for capteur in capteurs:
        if capteur.t_actif > higherTime:
            higherTime = capteur.t_actif

    energie = composants[0].p_actif*higherTime

    for capteur in capteurs:
        energie += capteur.p_actif*higherTime

    energie += composants[1].p_veille*higherTime

    return energie

def EnergieTraitement(composants,capteurs):
    higherTime = 100e-3

    energie = composants[0].p_actif*higherTime

    for capteur in capteurs:
        energie += capteur.p_reveil*higherTime

    energie += composants[1].p_veille*higherTime

    return energie

def EnergieReveilTransmetteur(composants,capteurs):
    higherTime = composants[1].t_reveil
    energie = higherTime*composants[1].t_reveil + higherTime*composants[0].t_actif
    for capteur in capteurs:
        energie+=capteur.p_veille*higherTime

    return energie

def EnergieTransmission(composants,capteurs):
    higherTime = 100e-3
    energie = higherTime*composants[1].t_actif + higherTime*composants[0].t_actif
    for capteur in capteurs:
        energie+=capteur.p_veille*higherTime
    
    return energie

def EnergieMiseEnVeil(composants,capteurs):
    higherTime = max(composants[0].t_reveil,composants[1].t_reveil)
    energie = higherTime*composants[1].t_reveil + higherTime*composants[0].t_actif
    for capteur in capteurs:
        energie+=capteur.p_veille*higherTime

    return energie

#Calcul d'energie total necessaire à un cycle
def calculerEnergie(composants,capteurs):
    energie = EnergieReveilMicrocontroleur(composants,capteurs)
    energie += EnergieReveilCapteurs(composants,capteurs)
    energie += EnergieMesures(composants,capteurs)
    energie += EnergieTraitement(composants,capteurs)
    energie += EnergieReveilTransmetteur(composants,capteurs)
    energie += EnergieTransmission(composants,capteurs)
    energie += EnergieMiseEnVeil(composants,capteurs)
    return energie 

#Calcul de puissance consommée aux differentes étapes du cycle
def PuissanceReveilMicrocontroleur(composants, Capteurs):
  P  = [composants[1].p_veille] +  [i.p_veille for i in Capteurs]
  P.append(composants[0].p_reveil)
  return sum(P), composants[0].t_reveil

def PuissanceReveilCapteurs(Composant, Capteurs):
  P = [i.p_reveil for i in Capteurs] + [Composant[0].p_actif] + [Composant[1].p_veille]
  T = [i.t_reveil for i in Capteurs]
  return sum(P), max(T)

def PuissanceMesures(Composant, Capteurs):
  P = [i.p_actif for i in Capteurs] + [Composant[0].p_actif] + [Composant[1].p_veille]
  T = [i.t_actif for i in Capteurs]
  return sum(P), max(T)

def PuissanceTraitementVeilCapeurs(Composant, Capteurs):
  P = [i.p_reveil for i in Capteurs] + [Composant[0].p_actif] + [Composant[1].p_veille]
  return sum(P), 100e-3

def PuissanceReveilEmmRecep(Composant, Capteurs):
  P = [i.p_veille for i in Capteurs] +[Composant[0].p_actif] + [Composant[1].p_reveil]
  T = Composant[1].t_reveil
  return sum(P), T

def PuissanceEnvoiDonnes(Composant, Capteurs):
  P = [i.p_veille for i in Capteurs] + [Composant[0].p_actif] + [Composant[1].p_actif]
  return sum(P), 100e-3

def PuissanceMiseVeil(Composant, Capteurs):
  P = [i.p_veille for i in Capteurs] + [Composant[0].p_reveil] + [Composant[1].p_reveil]
  T = [Composant[0].t_reveil] + [Composant[1].t_reveil]
  return sum(P), max(T)

#Fonction effectuant la simulation
def Simulate(Composants,Capteurs,btry,t):
    puissances = []
    temps = [0]
    energie = calculerEnergie(Composants,Capteurs)
    b = btry.charge_initial
    b_level = [btry.charge_initial]
    while(True):
        if b >= energie:
            P1, T1 = PuissanceReveilMicrocontroleur(composants, capteurs)
            puissances.append(P1)
            temps.append(temps[-1]+T1)
            b_level.append(b_level[-1] - P1*T1)
            if(temps[-1] > t):
                temps[-1] = t
                break
            P2, T2 = PuissanceReveilCapteurs(composants, capteurs)
            puissances.append(P2)
            temps.append(T2 + temps[-1])
            b_level.append(b_level[-1] - P2*T2)  
            if(temps[-1] > t):
                temps[-1] = t
                break
            P3, T3 = PuissanceMesures(composants, capteurs)
            puissances.append(P3)
            temps.append(T3 + temps[-1])
            b_level.append(b_level[-1] - P3*T3)
            if(temps[-1] > t):
                temps[-1] = t
                break
            P4, T4 = PuissanceTraitementVeilCapeurs(composants, capteurs)
            puissances.append(P4)
            temps.append(T4 + temps[-1])
            b_level.append(b_level[-1] - P4*T4) 
            if(temps[-1] > t):
                temps[-1] = t
                break
            P5, T5 = PuissanceReveilEmmRecep(composants, capteurs)
            puissances.append(P5)
            temps.append(T5 + temps[-1])
            b_level.append(b_level[-1] - P5*T5) 
            if(temps[-1] > t):
                temps[-1] = t
                break
            P6, T6 = PuissanceEnvoiDonnes(composants, capteurs)
            puissances.append(P6)
            temps.append(T6 + temps[-1])
            b_level.append(b_level[-1] - P6*T6) 
            if(temps[-1] > t):
                temps[-1] = t
                break
            P7, T7 = PuissanceMiseVeil(composants, capteurs)
            puissances.append(P7)
            temps.append(T7 + temps[-1])
            b_level.append(b_level[-1] - P7*T7)
            if(temps[-1] > t):
                temps[-1] = t
                break
            b = b - energie
            

        else:     
            puissances.append(composants[1].p_veille+composants[1].p_veille)
            for c in capteurs:
                puissances[-1]+=c.p_veille
            temps_recharge = (energie - b)/(btry.puissance_recharge - puissances[-1])
            temps.append(temps[-1]+temps_recharge)
            b_level.append(energie)
            if(temps[-1] > t):
                temps[-1] = t
                break
            else:
                b = energie
                
    return puissances,temps,b_level

#Fonction effectuant le tracé de graphique
def WSNPlot(puissances,temps,b_level):
    b_level = np.repeat(b_level,2)
    b_level = b_level[1:-1]
    pm=0
    for i in range(len(puissances)):
        pm += puissances[i]*(temps[i+1] - temps[i])

    pm = pm/temps[-1]

    puissances = np.repeat(puissances,2)
    temps = np.repeat(temps,2)

    for i in range(len(temps)):
        temps[i] += -((-1)^i)*1e-6

    temps = temps[1:-1]
    tpm = [temps[0],temps[-1]]
    pm = [pm,pm]

    fig,ax1 = plt.subplots()

    color = (1,0,0)
    ax1.set_xlabel('temps (s)')
    ax1.set_ylabel('Puissance (W)', color=color)
    ax1.plot(temps,puissances,color=color,label = 'Puissance consommée')
    ax1.plot(tpm,pm,color=(0,0,0),label = 'Puissance moyenne')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()

    color = (0,0,1)
    ax2.set_ylabel('Charge de la batterie (C)', color=color)
    ax2.plot(temps, b_level, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()
    fig.legend(loc='upper left')
    plt.show()

#Initialisation des variables globales dont on aura besoin pour l'interface graphique
cap_num = 0
capteurs_Label = []
capteurs_p1 = []
capteurs_p2 = []
capteurs_p3 = []
capteurs_p4 = []
capteurs_p5 = []
frames1 = []
frames2 = []
frames3 = []
frames4 = []
frames5 = []
units1 = []
units2 = []
units3 = []
units4 = []
units5 = []
time_val = ("s","ms","us")
pow_val = ("W","mW","uW")
multipliers = {"s":1,"ms":1e-3,"us":1e-6,"W":1,"mW":1e-3,"uW":1e-6}

# fonction permettant d'ajouter des capteurs à partir de l'interface graphique
def ajouterCapteur():
    global cap_num, capteurs_Label, capteurs_p1, capteurs_p2, capteurs_p3, capteurs_p4, capteurs_p5, frames1, frames2, frames3, frames4, frames5, units1, units2, units3, units4, units5
    capteurs_Label.append(0)
    capteurs_p1.append(0)
    capteurs_p2.append(0)
    capteurs_p3.append(0)
    capteurs_p4.append(0)
    capteurs_p5.append(0)
    frames1.append(0)
    frames2.append(0)
    frames3.append(0)
    frames4.append(0)
    frames5.append(0)
    units1.append(0)
    units2.append(0)
    units3.append(0)
    units4.append(0)
    units5.append(0)

    capteurs_Label[cap_num] = tkinter.Label(window,text = "Capteur "+str(cap_num+1))
    capteurs_Label[cap_num].grid(column=0,row=cap_num+3)

    frames1[cap_num] = tkinter.Frame(window)
    frames1[cap_num].grid(column=1,row=cap_num+3)
    capteurs_p1[cap_num] = tkinter.Entry(frames1[cap_num],width=5)
    capteurs_p1[cap_num].grid(column=0,row=0)
    units1[cap_num] = ttk.Combobox(frames1[cap_num],values=pow_val,width=3)
    units1[cap_num].grid(column=1,row=0)

    frames2[cap_num] = tkinter.Frame(window)
    frames2[cap_num].grid(column=2,row=cap_num+3)
    capteurs_p2[cap_num] = tkinter.Entry(frames2[cap_num],width=5)
    capteurs_p2[cap_num].grid(column=0,row=0)
    units2[cap_num] = ttk.Combobox(frames2[cap_num],values=time_val,width=3)
    units2[cap_num].grid(column=1,row=0)

    frames3[cap_num] = tkinter.Frame(window)
    frames3[cap_num].grid(column=3,row=cap_num+3)
    capteurs_p3[cap_num] = tkinter.Entry(frames3[cap_num],width=5)
    capteurs_p3[cap_num].grid(column=0,row=0)
    units3[cap_num] = ttk.Combobox(frames3[cap_num],values=pow_val,width=3)
    units3[cap_num].grid(column=1,row=0)

    frames4[cap_num] = tkinter.Frame(window)
    frames4[cap_num].grid(column=4,row=cap_num+3)
    capteurs_p4[cap_num] = tkinter.Entry(frames4[cap_num],width=5)
    capteurs_p4[cap_num].grid(column=0,row=0)
    units4[cap_num] = ttk.Combobox(frames4[cap_num],values=time_val,width=3)
    units4[cap_num].grid(column=1,row=0)

    frames5[cap_num] = tkinter.Frame(window)
    frames5[cap_num].grid(column=5,row=cap_num+3)
    capteurs_p5[cap_num] = tkinter.Entry(frames5[cap_num],width=5)
    capteurs_p5[cap_num].grid(column=0,row=0)
    units5[cap_num] = ttk.Combobox(frames5[cap_num],values=pow_val,width=3)
    units5[cap_num].grid(column=1,row=0)

    cap_num += 1

#Fonction permettant de prendre les valeurs par defaut ou les valeurs que l'utilisateur a indique sur l'interface graphique
def createComponents():
    global composants,capteurs,cap_num,btry,t_simulation, window
    try:
        btry = Baterie(float(btrChIntb.get()),float(btrPtb.get()))
        t_simulation = float(timess.get())*multipliers[timess_unit.get()]
        capteurs = []
        composants = [composant(float(p1_up.get())*multipliers[p1_unit.get()],float(p2_up.get())*multipliers[p2_unit.get()],float(p3_up.get())*multipliers[p3_unit.get()],float(p4_up.get())*multipliers[p4_unit.get()],float(p5_up.get())*multipliers[p5_unit.get()]),composant(float(p1_re.get())*multipliers[p1_unitre.get()] ,float(p2_re.get())*multipliers[p2_unitre.get()] ,float(p3_re.get())*multipliers[p3_unitre.get()] ,float(p4_re.get())*multipliers[p4_unitre.get()],float(p5_re.get())*multipliers[p5_unitre.get()])]
        for i in range(cap_num):
            capteurs.append(composant(float(capteurs_p1[i].get())*multipliers[units1[i].get()],float(capteurs_p2[i].get())*multipliers[units2[i].get()],float(capteurs_p3[i].get())*multipliers[units3[i].get()],float(capteurs_p4[i].get())*multipliers[units4[i].get()],float(capteurs_p5[i].get())*multipliers[units5[i].get()]))
    except ValueError:
        btry = Baterie(10,.1)
        t_simulation = 15
        composants = [composant(.15e-6,1.5,2.7e-6,100e-6,2.7e-6),composant(2.7e-6,100e-3,1e-3,350e-6,70.8e-3)]
        capteurs = [composant(4.86e-6,40e-9,1.08e-3,30e-9,1.08e-3),composant(25e-6,2e-3,1.875e-3,2e-3,1.875e-3)]

    window.destroy()

#Construction de l'interface graphique
window = tkinter.Tk()
window.title("Parametres de simulation")
window.geometry('800x300')

btr = tkinter.Label(window,text="Batterie:")
btr.grid(column=0, row=19)
btrChIn = tkinter.Label(window,text="Charge initiale (C): ")
btrChIn.grid(column=1, row=19)
btrChIntb = tkinter.Entry(window,width=5)
btrChIntb.grid(column=2,row=19)
btrP = tkinter.Label(window,text="Puissance de recharge (W): ")
btrP.grid(column=3, row=19)
btrPtb = tkinter.Entry(window,width=5)
btrPtb.grid(column=4,row=19)

tlabel = tkinter.Label(window,text="Temps de simulation:")
tlabel.grid(column=2,row=22)
frametemps = tkinter.Frame(window)
frametemps.grid(column=3,row=22)
timess = tkinter.Entry(frametemps,width=5)
timess.grid(column=0,row=0)
timess_unit = ttk.Combobox(frametemps,values=time_val,width=3)
timess_unit.grid(column=1,row=0)

lb1 = tkinter.Label(window, text="Puissance en veille:")
lb1.grid(column=1, row=0)
lb2 = tkinter.Label(window, text="Temps de reveil:")
lb2.grid(column=2, row=0)
lb1 = tkinter.Label(window, text="Puissance de reveil:")
lb1.grid(column=3, row=0)
lb2 = tkinter.Label(window, text="Temps actif:")
lb2.grid(column=4, row=0)
lb1 = tkinter.Label(window, text="Puissance actif:")
lb1.grid(column=5, row=0)
comp = tkinter.Label(window, text="Microprocesseur:")
comp.grid(column=0, row=1)

frame1 = tkinter.Frame(window)
frame1.grid(column=1,row=1)
p1_up = tkinter.Entry(frame1,width=5)
p1_up.grid(column=0,row=0)
p1_unit = ttk.Combobox(frame1,values=pow_val,width=3)
p1_unit.grid(column=1,row=0)

frame2 = tkinter.Frame(window)
frame2.grid(column=2,row=1)
p2_up = tkinter.Entry(frame2,width=5)
p2_up.grid(column=0,row=0)
p2_unit = ttk.Combobox(frame2,values=time_val,width=3)
p2_unit.grid(column=1,row=0)

frame3 = tkinter.Frame(window)
frame3.grid(column=3,row=1)
p3_up = tkinter.Entry(frame3,width=5)
p3_up.grid(column=0,row=0)
p3_unit = ttk.Combobox(frame3,values=pow_val,width=3)
p3_unit.grid(column=1,row=0)

frame4 = tkinter.Frame(window)
frame4.grid(column=4,row=1)
p4_up = tkinter.Entry(frame4,width=5)
p4_up.grid(column=0,row=0)
p4_unit = ttk.Combobox(frame4,values=time_val,width=3)
p4_unit.grid(column=1,row=0)

frame5 = tkinter.Frame(window)
frame5.grid(column=5,row=1)
p5_up = tkinter.Entry(frame5,width=5)
p5_up.grid(column=0,row=0)
p5_unit = ttk.Combobox(frame5,values=pow_val,width=3)
p5_unit.grid(column=1,row=0)

fram1 = tkinter.Frame(window)
fram1.grid(column=1,row=2)
p1_re = tkinter.Entry(fram1,width=5)
p1_re.grid(column=0,row=0)
p1_unitre = ttk.Combobox(fram1,values=pow_val,width=3)
p1_unitre.grid(column=1,row=0)

fram2 = tkinter.Frame(window)
fram2.grid(column=2,row=2)
p2_re = tkinter.Entry(fram2,width=5)
p2_re.grid(column=0,row=0)
p2_unitre = ttk.Combobox(fram2,values=time_val,width=3)
p2_unitre.grid(column=1,row=0)

fram3 = tkinter.Frame(window)
fram3.grid(column=3,row=2)
p3_re = tkinter.Entry(fram3,width=5)
p3_re.grid(column=0,row=0)
p3_unitre = ttk.Combobox(fram3,values=pow_val,width=3)
p3_unitre.grid(column=1,row=0)

fram4 = tkinter.Frame(window)
fram4.grid(column=4,row=2)
p4_re = tkinter.Entry(fram4,width=5)
p4_re.grid(column=0,row=0)
p4_unitre = ttk.Combobox(fram4,values=time_val,width=3)
p4_unitre.grid(column=1,row=0)

fram5 = tkinter.Frame(window)
fram5.grid(column=5,row=2)
p5_re = tkinter.Entry(fram5,width=5)
p5_re.grid(column=0,row=0)
p5_unitre = ttk.Combobox(fram5,values=pow_val,width=3)
p5_unitre.grid(column=1,row=0)



comp2 = tkinter.Label(window, text="Emetteur/recepteur:")
comp2.grid(column=0, row=2)
btn = tkinter.Button(window, text="Ajouter capteur",command=ajouterCapteur)
btn.grid(column=3, row=20)
btn = tkinter.Button(window, text="Lancer simulation",command=createComponents)
btn.grid(column=3, row=21)
window.mainloop()

#Lancement de la simulation et tracement de la courbe
puissances,temps,bat_l = Simulate(composants,capteurs,btry,t_simulation)
WSNPlot(puissances,temps,bat_l)
