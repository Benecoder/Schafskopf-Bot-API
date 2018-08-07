"""
Kartendarstellung

        Eichel  Grass   Herz    Schelle
7       10      20      30      40
8       11      21      31      41
9       12      22      32      42
10      13      23      33      43
unter   14      24      34      44
ober    15      25      35      45
könig   16      26      36      46
ass     17      27      37      47

"""
import random

#Liste der Trümpfe in absteigender Stich wertung
trumpf_wert = [15,25,35,45,14,24,34,44,
             37,33,36,32,31,30]
    
#stellt die farbe einer Karte fest
#Trumpf 0,Eichel 1,Gras 2,Herz 3,Schelle 4
def get_farbe(karte):
    if karte in trumpf_wert:
        return 0
    else:
        return karte//10


#entscheidet wer einen traditionellen sau Stich gewinnt
def argmaxsau(Stich):
    if Stich[0] not in trumpf_wert:
        farbe = Stich[0]//10
        farb_wert = [7,3,6,2,1,0]
        farb_wert = [farbe*10+i for i in farb_wert]
        gesamt_wert = trumpf_wert+farb_wert
    else:
        gesamt_wert = trumpf_wert
    
    for i in gesamt_wert:
        for j in range(4):
            if i == Stich[j]:
                return j
            
            
#rechnet wie viele Punkte in einem Stich sind
punkt_wert = {'0':0,'1':0,'2':0,'3':10,'4':2,'5':3,'6':4,'7':11}
def worth_stich(Stich):
    zeichen = [i%10 for i in Stich]
    punkte = [punkt_wert[str(i)] for i in zeichen]
    return sum(punkte)

class player():
    #hier kriegt es seinen namen
    def __init__(self,name):
        self.name = name
        
    #hier kriegt es karten ausgeteilt
    def handout(self,karten):
        self.karten = karten
        
    #hier sagt es ob es spielen will
    def call(self):
        self.spielt =  bool(random.getrandbits(1)) 
        return self.spielt
    
    #hier wird er gefragt auf wen es spielen will
    def target(self):
        a = random.choice([17,27,47])
        while a in self.karten:
            a = random.choice([17,27,47])
        return a
        
    #hier kriegt wer gesagt welcher spielmodus und wer auf wen gespielt wird
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
    def play(self,stich):
        if len(stich) == 0:
            karte = random.choice(self.karten)  #karte aussuchen
            self.karten.remove(karte)                      
            return karte                           #karte legen
        else:
            gespielte_farbe = get_farbe(stich[0])
            for karte in self.karten:
                if get_farbe(karte) == gespielte_farbe:
                    self.karten.remove(karte)
                    return karte
            karte = random.choice(self.karten)  #karte aussuchen
            self.karten.remove(karte) 
            return karte                           #karte legen
            
            
    
    #info über den Stich und an wen er gegangen ist
    def outcome(self,stich,winner):
        self.info = [stich,winner]
            
    
class game():
    def __init__(self,p1,p2,p3,p4,talkative = False):
        
        #Karten mischen
        self.karten = []
        for i in range(1,5):
            for j in range(8):
                self.karten.append(10*i+j)
        
        #Spieler erstellen
        self.players = [p1,p2,p3,p4]
        self.player_cards = []
        
        #Karten austeilen
        for i in range(4):
            self.players[i].handout(self.karten[i*8:(i+1)*8])
            self.player_cards.append(self.karten[i*8:(i+1)*8])
            
        self.gespielt = []
                
        #Testen wer spielt
        team_call  = []         
        for i in range(4):
            team_call.append(self.players[i].call())
        
        i = 0
        self.ramsch = False
        self.sau = False
        while not(self.ramsch) and not(self.sau):
            if i >= 4:
                self.ramsch = True
            elif team_call[i] != 0:
                self.sau = True
                self.spieler1 = i
            i += 1
        
        
        #jetzt wird gespielt
        if self.sau:

            #auf was wird gespielt
            self.angespielt = self.players[self.spieler1].target()
            assert self.angespielt not in self.player_cards[self.spieler1]     #verifiziert, dass es das ass nicht selber hat
            assert self.angespielt in [17,27,47]                               #verifiziert, dass es ein nicht-herz-ass ist
            for i in range(4):
                if self.angespielt in self.player_cards[i]:
                    self.spieler2 = i
            
            
            #sagt allen was abgeht
            for i in range(4):
                self.players[i].playmode([self.spieler1,self.angespielt])
            
            if talkative:
                print(self.players[self.spieler1].name +' würde ein Sau spiel auf ' +str(self.angespielt)+' spielen.')
                print(self.players[self.spieler2].name +' ist sein Mitspieler.')
            
            #spielt die Stiche
            punkte = [0,0,0,0]
            winner = 0 
            for i in range(8):
                reihenfolge = [0,1,2,3]
                reihenfolge = reihenfolge[winner:]+reihenfolge[:winner]
                
                Stich  = []
                    
                Stich.append(self.players[reihenfolge[0]].play(Stich))
                assert Stich[0] in self.player_cards[reihenfolge[0]]            #verifiziert, dass es die Karte nicht selber hat
                assert Stich[0] not in self.gespielt                            #verifiziert, dass die Karte nicht schon gespielt wurde
                self.player_cards[reihenfolge[0]].remove(Stich[0])
                self.gespielt.append(Stich[-1])
                
                farbe = get_farbe(Stich[0])
                
                for j in reihenfolge[1:]:
                    Stich.append(self.players[j].play(Stich))
                    
                    assert Stich[-1] in self.player_cards[j]                        #verifiziert, dass er die Karte selber hat
                    assert Stich[-1] not in self.gespielt                           #verifiziert, dass die Karte nicht schon gespielt wurde
                    kartenfarbe = get_farbe(Stich[-1])
                    if kartenfarbe != farbe:                                        #verifiziert, dass er nicht doch die richtige farbe hätte spielen können
                        mogliche_farben = [get_farbe(karte) for karte in self.player_cards[j]]
                        assert farbe not in mogliche_farben
                    self.player_cards[j].remove(Stich[-1])
                    
                winner = argmaxsau(Stich)
                punkte[winner] += worth_stich(Stich)
                for j in range(4):
                    self.players[j].outcome(Stich,winner)
            
            #Stellt fest wer gewonnen hat
            punkte_spieler = punkte[self.spieler1]+punkte[self.spieler2]
            if punkte_spieler>60:
                print(self.players[self.spieler1].name+' und '+self.players[self.spieler2].name+' haben das Spiel gewonnen.')
            else:
                winner = []
                for i in range(4):
                    if self.spieler1 != i and self.spieler2 != i:
                        winner.append(i)
                        
                print(self.players[winner[0]].name+' und '+self.players[winner[1]].name+' haben das Spiel nicht gewonnen.')
                    
                
        elif self.ramsch:

            #sagt allen was abgeht
            for i in range(4):
                self.players[i].playmode([0])
            
            if talkative:
                print('Ramsch!')
            
            #spielt die Stiche
            punkte = [0,0,0,0]
            winner = 0 
            for i in range(8):
                reihenfolge = [0,1,2,3]
                reihenfolge = reihenfolge[winner:]+reihenfolge[:winner]
                
                Stich  = []
                    
                Stich.append(self.players[reihenfolge[0]].play(Stich))
                assert Stich[0] in self.player_cards[reihenfolge[0]]            #verifiziert, dass es die Karte nicht selber hat
                assert Stich[0] not in self.gespielt                            #verifiziert, dass die Karte nicht schon gespielt wurde
                self.player_cards[reihenfolge[0]].remove(Stich[0])
                self.gespielt.append(Stich[-1])
                
                farbe = get_farbe(Stich[0])
                
                for j in reihenfolge[1:]:
                    Stich.append(self.players[j].play(Stich))
                    
                    assert Stich[-1] in self.player_cards[j]                        #verifiziert, dass er die Karte selber hat
                    assert Stich[-1] not in self.gespielt                           #verifiziert, dass die Karte nicht schon gespielt wurde
                    kartenfarbe = get_farbe(Stich[-1])
                    if kartenfarbe != farbe:                                        #verifiziert, dass er nicht doch die richtige farbe hätte spielen können
                        mogliche_farben = [get_farbe(karte) for karte in self.player_cards[j]]
                        assert farbe not in mogliche_farben
                    self.player_cards[j].remove(Stich[-1])
                    
                winner = argmaxsau(Stich)
                punkte[winner] += worth_stich(Stich)
                for j in range(4):
                    self.players[j].outcome(Stich,winner)
            
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
                

for _ in range(100):
    p1 = player('p1')
    p2 = player('p2')
    p3 = player('p3')
    p4 = player('p4')

    test_g = game(p1,p2,p3,p4,talkative = True)
