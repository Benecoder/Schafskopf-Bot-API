"""
Kartendarstellung

        Eichel  Grass   Herz    Schelle
7       10      20      30      40
8       11      21      31      41
9       12      22      32      42
koenig  13      23      33      43
10      14      24      34      44
sau     15      25      35      45
unter   16      26      36      46
ober    17      27      37      47

"""
import random

#Liste der Trümpfe in absteigender Stich wertung
spielbare_asse = [15,25,45]
punkt_wert = {0:0,1:0,2:0,3:4,4:10,5:11,6:2,7:3}


#Mögliche Farben/Werte
farbe=("Eichel", "Gras", "Herz", "Schelle")
wert=("7","8","9","Koenig","10","Sau","Unter","Ober")

#Darstellung im Bot
pos_kartenwert_id=[i for i in range(8)]
pos_kartenfarbe_id=[(j+1)*10 for j in range(4)]

karten_ids=[(i+j)for j in pos_kartenfarbe_id
        for  i in pos_kartenwert_id]

#Dictionary Karte und Kartenname
pos_kartenzeichen=dict(zip(pos_kartenwert_id,wert))
pos_kartenfarben=dict(zip(pos_kartenfarbe_id,farbe))
pos_kartennamen=dict(zip(karten_ids,[(j+"_"+i)for j in farbe 
                       for  i in wert]))



#stellt die farbe einer Karte fest
#Trumpf 0,Eichel 1,Gras 2,Herz 3,Schelle 4
def get_farbe(karte):
    return pos_kartenfarben[(karte//10)*10]
    
def get_punkte(karte):
    return punkt_wert[karte%10]

def get_zeichen(karte):
    return pos_kartenzeichen[karte%10]
    

class karte():
    def __init__(self, id):
        
        self.id = id
        self.farbe   = get_farbe(id)
        self.zeichen = get_zeichen(id) 
        self.wert    = get_punkte(id)
        self.name    = str(self.farbe)+'_'+str(self.zeichen)
        self.loc     = 'None'
    
    def trumpf_zuweisen(self,trumpfe):
        if self.id in trumpfe:
            self.trumpf = True
        else:
            self.trumpf = False
    
    #location encoding:
    #'None' - nicht ausgeteilt
    #str - name des Spielers
    #'Stich' - Im aktuellen Stich
    #'gespielt' - In einem vergangenen Stich
    def move_loc(self,loc):
        self.loc = loc

    
class game():
    def __init__(self,players,talkative):
        
        assert len(players) == 4
        self.players = players
        self.kartensatz = [karte(i) for i in karten_ids]
        self.trumpf_wert = [17,27,37,47,16,26,36,46,35,34,33,32,31,30]
        if talkative != None:
            self.talkative = talkative
        else:
            self.talkative = False
        
    def reset(self):
        random.shuffle(self.kartensatz)
        
        #Karten austeilen
        for i in range(4):
            self.players[i].handout(self.kartensatz[i*8:(i+1)*8])
            for j in self.kartensatz[i*8:(i+1)*8]:
                j.move_loc(self.players[i].name)
                
    #rechnet wie viele Punkte in einem Stich sind
    def worth_stich(self,Stich):
        punkte = [i.wert for i in Stich]
        return sum(punkte)
                
                
    #entscheidet wer ein traditionelles sau spiel gewinnt
    def argmaxsau(self,Stich):

        #setllt liste der Karten in absteigender Reihenfolge her
        if Stich[0].trumpf:
            gesamt_wert  =  self.trumpf_wert
        else:
            farb_wert = [i+10*(Stich[0].id//10) for i in range(5,-1,-1)]
            gesamt_wert = self.trumpf_wert+farb_wert

        for i in gesamt_wert:
            for j in range(4):
                if i == Stich[j].id:
                    return j
                
                
    def stechen(self):
    
            
            #spielt die Stiche
            punkte = [0,0,0,0]
            winner = 0 
            for i in range(8):
                reihenfolge = [0,1,2,3]
                reihenfolge = reihenfolge[winner:]+reihenfolge[:winner]
                
                Stich  = []
                    
                Stich.append(self.players[reihenfolge[0]].legen(Stich))
                assert Stich[0].loc == self.players[reihenfolge[0]].name        #verifiziert, dass es die Karte selber hat
                Stich[0].move_loc('Stich')
                
                for j in reihenfolge[1:]:
                    Stich.append(self.players[j].legen(Stich))
                    
                    assert Stich[-1].loc == self.players[j].name            #verifiziert, dass er die Karte selber hat
                    if Stich[-1].farbe != Stich[0].farbe:               #verifiziert, dass er nicht doch die richtige farbe hatte
                        for k in self.kartensatz:
                            assert k.loc != self.players[reihenfolge[0]].name or k.farbe != Stich[0].farbe or k.id == Stich[-1].id
                    
                    Stich[-1].move_loc('Stich')
                    
                    
                winner = self.argmaxsau(Stich)
                punkte[winner] += self.worth_stich(Stich)
                for j in range(4):
                    self.players[j].outcome(Stich)
                    
            return punkte

    
    def play(self):
        
                
        #Testen wer spielt
        player_calls  = []         
        for i in range(4):
            player_calls.append(self.players[i].call())
        
        
        #Entscheidet was gespielt wird
        i = 0
        ramsch = False
        sau = False
        while not(ramsch) and not(sau):
            if i >= 4:
                ramsch = True
            elif player_calls[i]==1:
                sau = True
                spieler = [i]
            i += 1
        
        #jetzt wird gespielt
        if sau:
            
            #Trumpfe deklarieren
            for i in self.kartensatz:
                if i in self.trumpf_wert:
                    i.trumpf = True
                else:
                    i.trumpf = False
            
            #auf was wird gespielt
            angespielt = self.players[spieler[0]].target()
            for i in self.kartensatz:
                if i.id == angespielt:
                    assert i.loc != self.players[spieler[0]].name           #verifiziert, dass es das ass nicht selber hat
                    assert i.id in spielbare_asse                           #verifiziert, dass das ass angespielt ist
            
            nicht_spieler = []
            for i in self.kartensatz:                                      #stellt fest wer die spieler sind...
                if angespielt == i.id:
                    for j in range(4):
                        if i.loc == self.players[j].name:
                            spieler.append(j)
                else:                                                       #...und wer nicht.
                    for j in range(4):
                        if i.loc == self.players[j].name:
                            nicht_spieler.append(j)
            
            #sagt allen was abgeht
            for i in range(4):
                self.players[i].playmode([spieler[0],angespielt])
            
            if self.talkative:
                print(self.players[spieler[0]].name +' würde ein Sau spiel auf ' +str(angespielt)+' spielen.')
                print(self.players[spieler[1]].name +' ist sein Mitspieler.')
            
            punkte = self.stechen()
                        
            #Stellt fest wer gewonnen hat
            punkte_spieler = punkte[spieler[0]]+punkte[spieler[1]]
            
            if punkte_spieler>60:
                print(self.players[spieler[0]].name+' und '+self.players[spieler[1]].name+' haben das Spiel gewonnen.')
            else:
                print(self.players[nicht_spieler[0]].name+' und '+self.players[nicht_spieler[1]].name+' haben das Spiel gewonnen.')
                        
            
        elif ramsch:
            
            #Trumpfe deklarieren
            for i in self.kartensatz:
                if i in self.trumpf_wert:
                    i.trumpf = True
                else:
                    i.trumpf = False

            for i in range(4):
                self.players[i].playmode([0])
            
            if self.talkative:
                print('Ramsch!')
                
            self.stechen()
            
            #Stellt fest wer verloren hat
            minimum = punkte[0]
            loser = 0
            durchmarsch = False
            for i in range(0,4):
                if punkte[i]<minimum:
                    loser = i
                    minimum = punkte[i]
                if punkte[i] > 90:
                    durchmarsch = True
                    winner = i
                    
            if not(durchmarsch):
                print(self.players[loser].name+' hat den Ramsch gewonnen.')
            else:
                print(self.players[winner].name+' hat einen Durchmarsch hingelegt.')

                
class player():
    #hier kriegt es seinen namen
    #Parameters:
    #   String
    def __init__(self,name):
        self.name = name
        
    #hier kriegt es karten ausgeteilt
    #Parameters:
    #   List of 8 objects of class 'karte'    
    def handout(self,karten):
        self.karten = karten
        self.karten_ids = [i.id for i in self.karten]
        
    #hier sagt es ob es spielen will    
    #must return:
    #   interger
    #0 - spielt nicht
    #1 - sau spiel
    def call(self):
        alle_asse = True
        for i in spielbare_asse:
            if i not in self.karten_ids:
                alle_asse = False
        
        if not(alle_asse):
            self.spielt =  bool(random.randint(0,1)) 
            return self.spielt
        else:
            return False
    
    #hier wird er gefragt auf wen es spielen will
    #must return:
    #   element of list spielbare_asse
    def target(self):
        a = random.choice(spielbare_asse)
        while a in self.karten_ids:
            a = random.choice(spielbare_asse)
        return a
        
    #hier kriegt wer gesagt welcher spielmodus und wer auf wen gespielt wird
    #Parameters:
    #   variying
    def playmode(self,info):
        #Format ist
        # len == 2 --> Sau spiel
        # element 1 ist welcher spieler als zahl
        # element 2 ist auf was also 17,27 oder 47
        # len == 1 --> und info[0] == 0
        # Ramsch
        
        self.info = info
        
    #hier kriegt es was liegt und muss sagen wie er reagiert
    #'stich' ist eine List der gelegten Karten in reihenfolge
    #Parameters:
    #   List of length between 0 and 3 of objects of class 'karte'
    #must return 
    #   object of class 'karte'
    def legen(self,stich):
        if len(stich) == 0:
            karte = random.choice(self.karten)  #karte aussuchen
            self.karten.remove(karte)    
            self.karten_ids.remove(karte.id)
            return karte                           #karte legen
        else:
            gespielte_farbe = stich[0].farbe
            for i in self.karten:
                if i.farbe == gespielte_farbe:
                    self.karten.remove(i)
                    self.karten_ids.remove(i.id)
                    return i
            karte = random.choice(self.karten)  #karte aussuchen
            self.karten.remove(karte)
            self.karten_ids.remove(karte.id)
            return karte                           #karte legen
            
            
    
    #info über den Stich und an wen er gegangen ist
    #Parameters:
    #   List of length 4 of objects of class 'karte'  
    def outcome(self,stich):
        self.info = stich
                
            

for _ in range(100):
    p1 = player('p1')
    p2 = player('p2')
    p3 = player('p3')
    p4 = player('p4')

    test_g = game([p1,p2,p3,p4],talkative = True)
    test_g.reset()
    test_g.play()
