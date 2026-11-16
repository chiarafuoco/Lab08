from calendar import month

from database.distributore_DAO import DistributoreDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        lista_medie = [] #inizializzo la lista di tuple

        for i in range(len(self._distributori)): #ciclo sulla lista dei distributori
            somma = 0 #inizializzo la somma per la media a 0 quando inizio il calcolo della media per ogni distributore
            num_giorni = 0 #faccio lo stesso per il numero di giorni
            prezzi = self._distributori[i].get_prezzi() #richiamo la funzione get_prezzi() per ottenere la lista di prezzi dell'anno per il distributore corrente
            for j in range(len(prezzi)): #ciclo per ogni prezzo (un prezzo al giorno)
                if prezzi[j].data.month == mese: # se il mese del giorno corrente è uguale al mese richiesto dall'utente
                    somma = somma + prezzi[j].prezzo_litro # aggiorno la somma mensile
                    num_giorni = num_giorni + 1 # aggiorno il numero di giorni nel mese
            media = somma/num_giorni # calcolo la media
            lista_medie.append((self._distributori[i].nome,round(media,3))) #aggiungo la tupla (nome,media_mese) nella lista
        #print(lista_medie)
        return lista_medie #returno la lista

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """

        if giorno > 7: # condizione per uscire dalla ricorsione
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo: # controllo se aggiornare il valore del costo ottimo e della relativa lista.
                #questo avviene o la prima volta che si arriva a 7 giorni (sequenza_parziale = [AAAAAAA], costo_ottimo=-1) o quando il costo è minore del costo ottimo
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = sequenza_parziale.copy() # faccio una copia per evitare che quando uso .pop() venga modificata
                return self.__costo_ottimo, self.__sequenza_ottima
        else:
            for i in range(len(self._distributori)): #controllo per ogni distributore
                id_distributore_corrente = self._distributori[i].id # salvo l'id del distributore corrente
                sequenza_parziale.append(id_distributore_corrente) #aggiungo l'id alla lista parziale
                nuovo_costo = costo_corrente + prezzi_settimana[id_distributore_corrente][giorno-1]*100 #calcolo il costo fisso e lo salvo in una variabile di supporto
                if ultimo_distributore != id_distributore_corrente and giorno >1: #aggiungo il costo nel caso in cui il distributore venga cambiato (valido dal secondo giorno in avanti)
                    nuovo_costo = nuovo_costo + 5

                self.__ricorsione(sequenza_parziale, giorno+1, id_distributore_corrente, nuovo_costo, prezzi_settimana) # chiamiamo la ricorsione aggiungendo +1 al giorno, usando il nuovo_costo come costo_corrente
                sequenza_parziale.pop() #elimino l'ultimo elemento per poter proseguire provare con un distributore diverso

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        dizionario_prezzi = {}
        for i in range(len(self._distributori)):  # ciclo sulla lista dei distributori
            lista_prezzi_primi_giorni = []
            prezzi = self._distributori[i].get_prezzi()  # richiamo la funzione get_prezzi() per ottenere la lista di prezzi dell'anno per il distributore corrente
            for j in range(len(prezzi)):  # ciclo per ogni prezzo (un prezzo al giorno)
                if prezzi[j].data.month == mese and prezzi[j].data.day < 8:  # se il mese del giorno corrente è uguale al mese richiesto dall'utente
                    lista_prezzi_primi_giorni.append(prezzi[j].prezzo_litro)
            dizionario_prezzi[self._distributori[i].id] = lista_prezzi_primi_giorni
        return dizionario_prezzi
