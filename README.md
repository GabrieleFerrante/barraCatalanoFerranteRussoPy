# barraCatalanoFerranteRussoPy
Il gruppo è formato da [Jorge Russo](https://github.com/Jo-333), [Gabriele Ferrante](http://github.com/GabrieleFerrante/ferrantePy), [Mario Barra](https://github.com/MarioBarra114/Barra.Py) e [Giovanni Catalano](https://github.com/giovannicatalano).

- [barraCatalanoFerranteRussoPy](#barracatalanoferranterussopy)
  - [**Requisiti**](#requisiti)
  - [**Descrizione**](#descrizione)
    - [**Le formule matematiche**](#le-formule-matematiche)
    - [**Logica del gioco**.](#logica-del-gioco)
  - [**Ruoli**](#ruoli)

</br>

## **Requisiti**

* Python 3.9 o 3.10
* Pygame
  * pygame_textinput
* Numpy
* Modulo Redis


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

La parabola realizzata in Python è sfruttata per calcolare la traiettoria delle frecce, passante per tre punti:  
* La posizione del giocatore
* La posizione del mouse che coincide con il vertice
* Il punto simmetrico rispetto alla posizione del giocatore

Per trovare i parametri *a*, *b* e *c* della traiettoria si risolve il sistema lineare di tre equazioni canoniche di una parabola, con i valori *x* e *y* sostituiti dalle coordinate dei suddetti tre punti.

### **Logica del gioco**.

![Diagramma della logica del gioco](https://github.com/GabrieleFerrante/barraCatalanoFerranteRussoPy/blob/main/diagramma-gioco.png?raw=true)

Il diagramma rappresenta la logica dietro al gioco.  

* **\_\_init\_\_()**: inizializza tutte le variabili del gioco, come le dimensioni della finestra, le vite o il punteggio;
* **title_screen()**: disegna e gestisce la schermata del titolo, con relativi pulsanti per iniziare una partita o visualizzare la classifica;
* **gameloop()**: loop del gioco, che gestisce tutti i processi principali di una partita;
  * **shoot()**: spara una freccia;
  * **Arrow()**: classe di una freccia;
    * **Arrow.update()**: aggiorna la posizione e l'angolazione; se esce dallo schermo o tocca il terreno cancellala;
    * **Arrow.check_collisions()**: controlla se la freccia collide con un bersaglio, se si cancellala, cancella il bersaglio e aumenta il punteggio;
  * **Target()**: classe di un bersaglio;
    * **Target.target_spawner()**: metodo di classe, crea periodicamente nuovi bersagli ad un'altezza casuale;
    * **Target.update()**: aggiorna la posizione del bersaglio, se esce dallo schermo togli una vita;
* **draw_all()**: disegna tutti gli elementi di gioco sullo schermo;
* **hud()**: disegna la *HUD*;
* **end_screen()**: disegna e gestisce la schermata di fine partita.


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

