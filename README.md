# barraCatalanoFerranteRussoPy
Il gruppo è formato da [Jorge Russo](https://github.com/Jo-333), [Gabriele Ferrante](http://github.com/GabrieleFerrante/ferrantePy), [Mario Barra](https://github.com/MarioBarra114/Barra.Py) e [Giovanni Catalano](https://github.com/giovannicatalano).

- [barraCatalanoFerranteRussoPy](#barracatalanoferranterussopy)
  - [**Requisiti**](#requisiti)
  - [**Descrizione**](#descrizione)
    - [**Le formule matematiche**](#le-formule-matematiche)
    - [**Logica del gioco**.](#logica-del-gioco)
  - [**Problemi noti**](#problemi-noti)
  - [**Ruoli**](#ruoli)

</br>

## **Requisiti**

* Python 3.9 o 3.10
* Pygame
* Numpy


## **Descrizione**

L'idea consiste in un gioco di tiro al bersaglio con visuale laterale. Il giocatore deve colpire dei bersagli che arriveranno costantemente scoccando delle frecce. Colpendo i bersagli il punteggio aumenta.  
Se un bersaglio non viene colpito in tempo ed esce dallo schermo il giocatore perderà una vita. La partita termina quando il giocatore finisce le vite.  
All'inizio della partita il giocatore seleziona uno tra tre livelli di difficoltà:

* **FACILE**: 5 vite
* **NORMALE**: 3 vite
* **DIFFICILE**: 1 vita  

L'obiettivo del gioco è realizzare il punteggio più alto possibile. I tre record per ogni difficoltà verranno ipoteticamente salvati su un database remoto alla fine di ogni partita.  
Grazie a ciò sarà possibile comparare i migliori punteggi realizzati dai giocatori, visualizzabili da una classifica in gioco.


### **Le formule matematiche**

La traiettoria delle frecce sfrutta la parabola realizzata in Python, passante per tre punti:  
* La posizione del giocatore
* La posizione del mouse che coincide con il vertice
* Il punto simmetrico rispetto alla posizione del giocatore

Per trovare i parametri *a*, *b* e *c* della traiettoria si risolve il sistema lineare di tre equazioni canoniche di una parabola, con i valori *x* e *y* sostituiti dalle coordinate dei suddetti tre punti.

### **Logica del gioco**.

![Diagramma della logica del gioco](https://github.com/GabrieleFerrante/barraCatalanoFerranteRussoPy/blob/main/diagramma-gioco.png?raw=true)


## **Problemi noti**

* Le collisioni tra frecce e bersagli non funzionano correttamente


## **Ruoli**

*Russo*:
* Gestione e realizzazione del software
* Scrittura del file README
* Progettazione

*Barra*: 
* Gestione e realizzazione del software
* Progettazione

*Ferrante*: 
* Gestione e realizzazione del software
* Scrittura del file README
* Progettazione

*Catalano*: 
* Gestione e realizzazione del software
* Progettazione

