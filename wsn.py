import matplotlib.pyplot as plt
import numpy as np

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

composants = [composant(0.15e-6,1.5,2.7e-6,1,2.7e-6),composant(2.7e-6,2,50e-5,3,70.8e-5)]
capteurs = [composant(4.86e-6,.5,1.08e-3,1.2,2e-3),composant(25e-6,.5,1.875e-3,1.2,1.575e-3)]
btry = Baterie(13,1)
t_simulation = 30

puissances,temps,pm = Simulate(composants,capteurs,btry,t_simulation)
WSNPlot(puissances,temps)

