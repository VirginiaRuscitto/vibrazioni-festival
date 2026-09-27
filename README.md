# Vibrazioni Festival

Applicazione web full-stack dedicata alla gestione di un festival musicale di 3 giorni (venerdì, sabato e domenica) su 3 palchi paralleli e due tipologie di utenti: partecipanti e organizzatori. I partecipanti possono consultare il programma delle esibizioni, filtrarlo per giorno, genere e palco e acquistare un biglietto, mentre gli organizzatori possono aggiungere artisti, creare e pubblicare performance, salvarle come bozze, modificarle o eliminarle.

---

## Funzionalità principali

- Autenticazione e gestione sessioni con `Flask-Login`
- Gestione di due ruoli utente: partecipante e organizzatore
- Consultazione e filtraggio del programma per giorno, genere e palco
- Acquisto dei biglietti con controllo del numero massimo di presenze giornaliere
- Gestione delle performance:
  - creazione e modifica
  - salvataggio come bozza o pubblicazione
  - validazione dei dati e della durata
  - controllo delle sovrapposizioni sullo stesso palco
  - upload di una copertina e di foto aggiuntive
- Gestione anagrafica artisti con controllo dei duplicati e biografia opzionale
- Pagina del profilo dinamica in base al ruolo, con statistiche di vendita per gli organizzatori e riepilogo del biglietto per i partecipanti
- Ridimensionamento automatico delle immagini tramite `Pillow`

## Stack tecnico

| Livello | Tecnologie |
|---|---|
| Backend | `Python`, `Flask`, `Flask-Login` |
| Database | `SQLite` |
| Frontend | `HTML5`, `Jinja2`, `CSS3`, `Bootstrap 5` |
| Elaborazione immagini | `Pillow` |

## Database

**UTENTI:** (id (PK), email (UNIQUE), password, nome, cognome, is_partecipante)

**ARTISTI:** (id (PK), nome (UNIQUE), foto_profilo, biografia)

**PALCHI:** (id (PK), nome (UNIQUE))

**GENERI:** (id (PK), nome (UNIQUE))

**PERFORMANCE:** (id (PK), id_artista (FK → artisti.id), id_organizzatore (FK → utenti.id), id_palco (FK → palchi.id), id_genere (FK → generi.id), giorno_inizio, ora_inizio, giorno_fine, ora_fine, immagine_copertina, is_pubblicata, durata, descrizione)

**FOTO_PERFORMANCE:** (id (PK), id_performance (FK → performance.id), foto)

**BIGLIETTI:** (id (PK), nome, venerdi, sabato, domenica, descrizione, nome_visualizzato)

**ACQUISTI_BIGLIETTI:** (id_utente (PK, FK → utenti.id), id_biglietto (FK → biglietti.id), data_acquisto, ora_acquisto)

---

## Screenshot

### Home
![Home](screenshots/Home.PNG)

### Acquisto biglietti
![Acquisto biglietti](screenshots/Acquisto-biglietto.PNG)

### Nuova performance
![Nuova performance](screenshots/Nuova-performance.PNG)

---

## Credenziali di test

Sono disponibili alcuni account preconfigurati per provare le funzionalità dei due ruoli.

| Email | Password | Ruolo |
|---|---|---|
| matteo.rossi@example.com | matteo01 | Organizzatore |
| martina.bianchi@example.com | martina01 | Organizzatore |
| federico.conti@example.com | federico01 | Partecipante |
| eleonora.moretti@example.com | eleonora01 | Partecipante |
| lorenzo.ferrari@example.com | lorenzo01 | Partecipante |

## Avvio in locale
Installare le dipendenze con:
```bash
pip install -r requirements.txt
```
Avviare l'applicazione con:
```bash
flask run
```
L'app sarà disponibile su `http://127.0.0.1:5000`.

## Configurazione
La versione del progetto presente in questa repository corrisponde alla versione consegnata per l'esame. La `SECRET_KEY` viene definita direttamente nel codice a scopi didattici e in un'applicazione reale dovrebbe essere mantenuta separata dal codice sorgente, ad esempio tramite variabili d'ambiente.
