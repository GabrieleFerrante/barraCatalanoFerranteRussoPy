# **Changelog**

Cambiamenti relativi al gioco in Python  

## **[0.5.2]**
---
* Aggiunta la classifica
* Ora passare il cursore sopra un bersaglio mostra la sua equazione della retta


## **[0.5.1]**
---
* Risolto un bug dove se si cambiava il nome prima di chiudere il gioco, al prossimo avvio i dati non sarebbero stati sincronizzati correttamente


## **[0.5.0]**
---
* Aggiunto il salvataggio dati su database remoto, basato su un id generato al primo avvio del gioco.
* Ora il giocatore deve scegliere un nome al primo avvio del gioco. Questo può essere modificato in seguito.
* Aggiunta una schermata di fine partita, che mostra il punteggio raggiunto.


## **[0.4.1]**
---
* Ora l'equazione della traiettoria è visualizzata durante il gioco


## **[0.4.0]**
---
* Aggiunto il menu principale
  * Il nome BIG SHOT non è definitivo
* Aggiunta la possibilità di mettere in pausa il gioco
* Aggiunto uno sfondo con un effetto di parallasse
* La HUD ora mostra le vite rimanenti
* Aggiunto il record
  * Al momento il record non è salvato alla chiusura del gioco
* Ora si può selezionare la difficoltà tra FACILE, NORMALE, DIFFICILE
  * Il record differisce tra le tre difficoltà

## **[0.3.2]**
---
* Risolti i problemi di collisione delle frecce
* Aggiornati gli sprite di:
  * Frecce
  * Bersagli
  * Terreno
* Riordinato il codice di gioco

## **[0.3.1]**
---
* Risolto un problema che causava un crash all'avvio su sistemi operativi diversi da Windows
* Riordinato il codice di gioco


## **[0.3.0]**
---
* Aggiunte le collisioni delle frecce con i bersagli
* Bilanciata la velocità delle frecce


## **[0.2.0]**
---

* Introdotto il punteggio
* Introdotte le vite
  * Rimosse quando un bersaglio esce dallo schermo
* Introdotta una basica *HUD*
* Ridotta la velocità dei bersagli
* Risolto un bug della rotazione delle frecce che causava un crash
* Riordinato il codice
### **To do**
* Collisioni delle frecce con i bersagli


## **[0.1.2]**
---

* Aggiunta la rotazione delle frecce
* Tempo di creazione dei bersagli aumentato da *3,0s* a *3,5s*
* Ripulito il codice


## **[0.1.1]**
---

* Possibilità di scoccare una freccia usando la traiettoria parabolica


## **[0.1.0]**
---

* Base del gioco con:
  * Sistema di creazione dei bersagli
  * Calcolo della traiettoria con la parabola passante per tre punti
  * Terreno animato
