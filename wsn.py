import matplotlib.pyplot as plt
import matplotlib
import tkinter
import numpy as np

matplotlib.use('TkAgg')

class composant:
    def __init__(self,p_veille,t_reveil,p_reveil,t_actif,p_actif):
        self.p_veille = p_veille
        self.t_reveil = t_reveil
        self.p_reveil = p_reveil
        self.t_actif = t_actif
        self.p_actif = p_actif

class Baterie:
    def __init__(self,charge_initial,puissance_recharge):
        self.charge_initial = charge_initial
        self.puissance_recharge = puissance_recharge 

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

def calculerEnergie(composants,capteurs):
    energie = EnergieReveilMicrocontroleur(composants,capteurs)
    energie += EnergieReveilCapteurs(composants,capteurs)
    energie += EnergieMesures(composants,capteurs)
    energie += EnergieTraitement(composants,capteurs)
    energie += EnergieReveilTransmetteur(composants,capteurs)
    energie += EnergieTransmission(composants,capteurs)
    energie += EnergieMiseEnVeil(composants,capteurs)
    return energie 

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

def Simulate(Composants,Capteurs,btry,t):
    puissances = []
    temps = [0]
    energie = calculerEnergie(Composants,Capteurs)
    b = btry.charge_initial
    while(True):
        if b >= energie:
            P1, T1 = PuissanceReveilMicrocontroleur(composants, capteurs)
            puissances.append(P1)
            temps.append(temps[-1]+T1)
            pm = energie/T1
            if(temps[-1] > t):
                temps[-1] = t
                break
            P2, T2 = PuissanceReveilCapteurs(composants, capteurs)
            puissances.append(P2)
            temps.append(T2 + temps[-1])
            pm = energie/T2
            if(temps[-1] > t):
                temps[-1] = t
                break
            P3, T3 = PuissanceMesures(composants, capteurs)
            puissances.append(P3)
            temps.append(T3 + temps[-1])
            pm = energie/T3
            if(temps[-1] > t):
                temps[-1] = t
                break
            P4, T4 = PuissanceTraitementVeilCapeurs(composants, capteurs)
            puissances.append(P4)
            temps.append(T4 + temps[-1])
            pm = energie/T4
            if(temps[-1] > t):
                temps[-1] = t
                break
            P5, T5 = PuissanceReveilEmmRecep(composants, capteurs)
            puissances.append(P5)
            temps.append(T5 + temps[-1])
            pm = energie/T5
            if(temps[-1] > t):
                temps[-1] = t
                break
            P6, T6 = PuissanceEnvoiDonnes(composants, capteurs)
            puissances.append(P6)
            temps.append(T6 + temps[-1])
            pm = energie/T6
            if(temps[-1] > t):
                temps[-1] = t
                break
            P7, T7 = PuissanceMiseVeil(composants, capteurs)
            puissances.append(P7)
            temps.append(T7 + temps[-1])
            pm = energie/T7
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
            if(temps[-1] > t):
                temps[-1] = t
                break
            else:
                b = energie
                
    return puissances,temps,pm

def WSNPlot(puissances,temps):
    pm = [sum(puissances)/temps[-1],sum(puissances)/temps[-1]]
    t_pm = [temps[0],temps[-1]] 
    puissances = np.repeat(puissances,2)
    temps = np.repeat(temps,2)

    for i in range(len(temps)):
        temps[i] += -((-1)^i)*1e-6

    temps = temps[1:-1]
    plt.plot(temps,puissances)
    plt.plot(t_pm,pm)
    plt.autoscale(enable=True, axis='x', tight=True)
    plt.title("Simulation of WSN")
    plt.xlabel("Temps (s)")
    plt.ylabel("Puissance (W)")
    plt.show()

cap_num = 0
capteurs_Label = []
capteurs_p1 = []
capteurs_p2 = []
capteurs_p3 = []
capteurs_p4 = []
capteurs_p5 = []


def ajouterCapteur():
    global cap_num, capteurs_Label, capteurs_p1, capteurs_p2, capteurs_p3, capteurs_p4, capteurs_p5
    capteurs_Label.append(0)
    capteurs_p1.append(0)
    capteurs_p2.append(0)
    capteurs_p3.append(0)
    capteurs_p4.append(0)
    capteurs_p5.append(0)
    capteurs_Label[cap_num] = tkinter.Label(window,text="Capteur " + str(cap_num + 1))
    capteurs_Label[cap_num].grid(column=0,row=cap_num+3)
    capteurs_p1[cap_num] = tkinter.Entry(window,width=5)
    capteurs_p1[cap_num].grid(column=1,row=cap_num+3)
    capteurs_p2[cap_num] = tkinter.Entry(window,width=5)
    capteurs_p2[cap_num].grid(column=2,row=cap_num+3)
    capteurs_p3[cap_num] = tkinter.Entry(window,width=5)
    capteurs_p3[cap_num].grid(column=3,row=cap_num+3)
    capteurs_p4[cap_num] = tkinter.Entry(window,width=5)
    capteurs_p4[cap_num].grid(column=4,row=cap_num+3)
    capteurs_p5[cap_num] = tkinter.Entry(window,width=5)
    capteurs_p5[cap_num].grid(column=5,row=cap_num+3)
    print(p1_up.get())

    cap_num += 1

def createComponents():
    global composants,capteurs,cap_num
    capteurs = []
    composants = [composant(float(p1_up.get()),float(p2_up.get()),float(p3_up.get()),float(p4_up.get()),float(p5_up.get())),composant(float(p1_er.get()),float(p2_er.get()),float(p3_er.get()),float(p4_er.get()),float(p5_er.get()))]
    for i in range(cap_num):
        capteurs.append(composant(capteurs_p1[i],capteurs_p2[i],capteurs_p3[i],capteurs_p4[i],capteurs_p5[i]))

    print(capteurs)


window = tkinter.Tk()
window.title("Parametres de simulation")
window.geometry('800x300')

lb1 = tkinter.Label(window, text="Puissance en veille (W):")
lb1.grid(column=1, row=0)
lb2 = tkinter.Label(window, text="Temps de reveil (s):")
lb2.grid(column=2, row=0)
lb1 = tkinter.Label(window, text="Puissance de reveil (W):")
lb1.grid(column=3, row=0)
lb2 = tkinter.Label(window, text="Temps actif (s):")
lb2.grid(column=4, row=0)
lb1 = tkinter.Label(window, text="Puissance actif (W):")
lb1.grid(column=5, row=0)
comp = tkinter.Label(window, text="Microprocesseur:")
comp.grid(column=0, row=1)
p1_up = tkinter.Entry(window,width=5)
p1_up.grid(column=1,row=1)
p2_up = tkinter.Entry(window,width=5)
p2_up.grid(column=2,row=1)
p3_up = tkinter.Entry(window,width=5)
p3_up.grid(column=3,row=1)
p4_up = tkinter.Entry(window,width=5)
p4_up.grid(column=4,row=1)
p5_up = tkinter.Entry(window,width=5)
p5_up.grid(column=5,row=1)
p1_er = tkinter.Entry(window,width=5)
p1_er.grid(column=1,row=2)
p2_er = tkinter.Entry(window,width=5)
p2_er.grid(column=2,row=2)
p3_er = tkinter.Entry(window,width=5)
p3_er.grid(column=3,row=2)
p4_er = tkinter.Entry(window,width=5)
p4_er.grid(column=4,row=2)
p5_er = tkinter.Entry(window,width=5)
p5_er.grid(column=5,row=2)
comp2 = tkinter.Label(window, text="Emetteur/recepteur:")
comp2.grid(column=0, row=2)
btn = tkinter.Button(window, text="Ajouter capteur",command=ajouterCapteur)
btn.grid(column=3, row=20)
btn = tkinter.Button(window, text="Lancer simulation",command=createComponents)
btn.grid(column=3, row=21)
window.mainloop()
  
btry = Baterie(13,1)
t_simulation = 30

puissances,temps,pm = Simulate(composants,capteurs,btry,t_simulation)
#WSNPlot(puissances,temps)
