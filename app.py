from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from models import User
import dao.utenti_dao as utenti_dao, dao.biglietti_dao as biglietti_dao, dao.acquisti_biglietti_dao as acquisti_biglietti_dao, dao.others_dao as others_dao, dao.performance_dao as performance_dao
from PIL import Image
import time
import re

FOTO_PROFILO_HEIGHT = 200
FOTO_PERFORMANCE_HEIGHT = 700

MAX_BIGLIETTI_GIORNATA = 200
GIORNI_FESTIVAL = {
    'venerdi': 'venerdì',
    'sabato': 'sabato',
    'domenica': 'domenica'
}
ORDINE_GIORNI = ['venerdi', 'sabato', 'domenica']

app = Flask(__name__)

app.config['SECRET_KEY'] = 'Vibrazioni festival 2025'

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/', methods=['GET'])
def home():
    giorno = request.args.get('giorno', default=None)
    id_genere = request.args.get('id_genere', default=None)
    id_palco = request.args.get('id_palco', default=None)

    performance = performance_dao.get_performance(giorno=giorno, id_genere=id_genere, id_palco=id_palco)

    risultati = []
    for row in performance:
        r = dict(row)
        r['giorno_inizio'] = GIORNI_FESTIVAL.get(r['giorno_inizio'], r['giorno_inizio'])
        r['giorno_fine'] = GIORNI_FESTIVAL.get(r['giorno_fine'], r['giorno_fine'])
        risultati.append(r)

    return render_template(
        'home.html',
        p_performance=risultati,
        p_generi=others_dao.get_generi(),
        p_palchi=others_dao.get_palchi(),
        p_giorni_festival=GIORNI_FESTIVAL,
        filtro_giorno=giorno,
        filtro_genere=id_genere,
        filtro_palco=id_palco
    )

@app.route('/performance/<int:id>')
def performance(id):
    performance = performance_dao.get_performance_by_id(id)
    
    if performance is None:
        flash('Performance non trovata', 'danger')
        return redirect(url_for('home'))
    
    p = dict(performance)
    p['giorno_inizio'] = GIORNI_FESTIVAL.get(p['giorno_inizio'], p['giorno_inizio'])
    p['giorno_fine'] = GIORNI_FESTIVAL.get(p['giorno_fine'], p['giorno_fine'])

    return render_template('performance.html', p_performance=p, p_foto=others_dao.get_foto_by_performance(id))

@app.route('/biglietti')
#il controllo di @login_required lo faccio dentro la funzione per poter mandare il flash alle persone non registrate
def biglietti():
    if not check_partecipante():
        flash("Per accedere a questa pagina è necessario essere registrati come partecipanti", "danger")
        return redirect(request.referrer or url_for('home'))
    
    primo_biglietto = not ha_gia_biglietto()
    if not primo_biglietto:
        flash("Non è possibile acquistare più di un biglietto", "danger")

    return render_template('biglietti.html', p_biglietti_distinti=biglietti_dao.get_biglietti_distinti(), p_primo_biglietto=primo_biglietto)

@app.route('/biglietti/<nome>')
@login_required
def biglietto(nome):
    if not check_partecipante():
        flash("Per accedere a questa pagina è necessario essere registrati come partecipanti", "danger")
        return redirect(url_for('home'))
    
    if ha_gia_biglietto():
        flash("Non è possibile acquistare più di un biglietto", "danger")
        return redirect(url_for('home'))
    
    nomi_distinti = [row['nome'] for row in biglietti_dao.get_biglietti_distinti()]
    
    if nome not in nomi_distinti:
        flash('Nome del biglietto non valido', 'danger')
        return redirect(url_for('biglietti'))

    opzioni_biglietto = biglietti_dao.get_biglietti_by_nome(nome)
    if not opzioni_biglietto:
        flash('Biglietto non trovato', 'danger')
        return redirect(url_for('biglietti'))
    
    venduti_per_giorno = {
        giorno: acquisti_biglietti_dao.conta_biglietti_venduti(giorno)
        for giorno in GIORNI_FESTIVAL
    }

    opzioni_biglietto_finale = []
    for opzione in opzioni_biglietto:
        opzione_dict = dict(opzione)
        opzione_dict['giorni_bin'] = giorni_to_bin_str(opzione)
        opzione_dict['disabilitato'] = any(
            opzione_dict[giorno] != 0 and venduti_per_giorno[giorno] >= MAX_BIGLIETTI_GIORNATA
            for giorno in ORDINE_GIORNI
        )
        opzioni_biglietto_finale.append(opzione_dict)

    return render_template('biglietto.html', p_opzioni=opzioni_biglietto_finale, p_giorni_festival=GIORNI_FESTIVAL)

@app.route('/acquista-biglietto', methods=['POST'])
@login_required
def acquista_biglietto():
    if not check_partecipante():
        flash('Solo chi è registrato come partecipante può acquistare i biglietti', 'danger')
        return redirect(url_for('home'))
    
    if ha_gia_biglietto():
        flash('Non è possibile acquistare più di un biglietto', 'danger')
        return redirect(url_for('biglietti'))
    
    biglietto_form = request.form.to_dict()
    tipo = biglietto_form.get('tipo_biglietto')
    giorni = biglietto_form.get('giorni')

    if not tipo or not giorni or len(giorni) != len(GIORNI_FESTIVAL) or not set(giorni).issubset({'0', '1'}):
        flash('I dati del biglietto sono errati', 'danger')
        return redirect(url_for('biglietti'))

    giorni_attivi = [giorno for giorno, bit in zip(ORDINE_GIORNI, giorni) if bit == '1']
    if any(acquisti_biglietti_dao.conta_biglietti_venduti(giorno) >= MAX_BIGLIETTI_GIORNATA for giorno in giorni_attivi):
        flash('Limite massimo di biglietti raggiunto per almeno un giorno selezionato', 'danger')
        return redirect(url_for('biglietti'))

    giorni_int = tuple(int(bit) for bit in giorni)
    id_biglietto = biglietti_dao.trova_id_biglietto(tipo, *giorni_int)
    if not id_biglietto:
        flash('Errore nella procedura di acquisto del biglietto: riprovare', 'danger')
        return redirect(url_for('biglietti'))
    id_biglietto = int(id_biglietto['id'])
    
    now = datetime.now()
    data = now.strftime('%Y-%m-%d')
    ora = now.strftime('%H:%M:%S')
    success = acquisti_biglietti_dao.acquista_biglietto(id_biglietto, current_user.id, data, ora)
    if success:
        flash('Acquisto effettuato con successo', 'success')
        return redirect(url_for('profilo'))
    else:
        flash('Errore nella procedura di acquisto del biglietto: riprovare', 'danger')
        return redirect(url_for('biglietti'))
    
@app.route('/profilo')
@login_required
def profilo():
    if check_partecipante():
        acquisto = acquisti_biglietti_dao.get_biglietto_by_id_utente(current_user.id)
        id = None
        biglietto = None
        if acquisto:
            id = acquisto['id_biglietto']
            biglietto=biglietti_dao.get_biglietto_by_id(id)
            biglietto = dict(biglietto)
            giorni_validi = [GIORNI_FESTIVAL[g] for g in ORDINE_GIORNI if biglietto.get(g, 0) == 1]
            if len(giorni_validi) == 0:
                giorni_str = ""
            elif len(giorni_validi) == 1:
                giorni_str = giorni_validi[0]
            else:
                giorni_str = ", ".join(giorni_validi[:-1]) + " e " + giorni_validi[-1]
            biglietto['giorni_validi_str'] = giorni_str

        return render_template('profilo.html', p_utente=current_user, p_acquisto=acquisto, p_biglietto=biglietto)
    
    else:
        statistiche = [
            {
                'nome_giorno': GIORNI_FESTIVAL[giorno],
                'biglietti_venduti': acquisti_biglietti_dao.conta_biglietti_venduti(giorno)
            }
            for giorno in ORDINE_GIORNI
        ]

        performance = performance_dao.get_performance()
        risultati = []
        for row in performance:
            r = dict(row)
            r['giorno_inizio'] = GIORNI_FESTIVAL.get(r['giorno_inizio'], r['giorno_inizio'])
            r['giorno_fine'] = GIORNI_FESTIVAL.get(r['giorno_fine'], r['giorno_fine'])
            risultati.append(r)

        return render_template(
            'profilo.html',
            p_utente=current_user,
            p_statistiche=statistiche,
            p_max_biglietti=MAX_BIGLIETTI_GIORNATA,
            p_bozze=performance_dao.get_bozze_by_organizzatore(current_user.id),
            p_performance=risultati
        )

@app.route('/nuova-performance', methods=['GET'])
@login_required
def nuova_performance():
    if check_partecipante():
        flash("Solo chi è registrato come organizzatore può creare una nuova performance", "danger")
        return redirect(url_for('home'))

    id_bozza = request.args.get('id_bozza')
    bozza = None
    id_artista_bozza = None

    if id_bozza:
        bozza = performance_dao.get_bozza_by_id(id_bozza)
        if bozza:
            bozza = dict(bozza)
            id_artista_bozza = bozza.get('id_artista')
        if not bozza or bozza.get('is_pubblicata') != 0 or bozza.get('id_organizzatore') != current_user.id:
            flash("Bozza non trovata o accesso non autorizzato", "danger")
            return redirect(url_for('profilo'))
        
    artisti = others_dao.get_artisti()
    artisti_occupati = performance_dao.get_id_artisti_occupati()
    # Se stiamo modificando una bozza non si esclude l'artista della bozza anche se è occupato
    artisti_disponibili = [
        a for a in artisti
        if a['id'] not in artisti_occupati or a['id'] == id_artista_bozza
    ]

    foto = None
    if id_bozza:
        foto = others_dao.get_foto_by_performance(id_bozza)

    return render_template(
        'new_performance.html',
        p_artisti=artisti_disponibili,
        p_palchi=others_dao.get_palchi(),
        p_generi=others_dao.get_generi(),
        p_giorni_festival=GIORNI_FESTIVAL,
        p_bozza=bozza,
        p_foto=foto
    )

@app.route('/nuova-performance', methods=['POST'])
@login_required
def nuova_performance_post():
    if check_partecipante():
        flash("Solo chi è registrato come organizzatore può creare una nuova performance", "danger")
        return redirect(url_for('home'))
    
    id_bozza = request.form.get("is_bozza")
    performance_form = request.form.to_dict()
    bozza = None
    if id_bozza:
        bozza = performance_dao.get_bozza_by_id(id_bozza)
        if bozza:
            bozza = dict(bozza)
    
    campi_necessari = ['id_artista', 'giorno_inizio', 'ora_inizio', 'giorno_fine', 'ora_fine', 'id_palco', 'id_genere', 'descrizione', 'tipo_performance']
    immagine_copertina = request.files.get('immagine_copertina')

    if any(not performance_form.get(campo) for campo in campi_necessari) or (not bozza and (not immagine_copertina or immagine_copertina.filename == "")):
        flash('Non sono stati compilati tutti i campi per registrare la performance', 'danger')
        return redirect(url_for('nuova_performance'))

    if not others_dao.get_artista_by_id(performance_form.get('id_artista')):
        flash("L'artista selezionato non fa parte del database del festival, è necessario prima aggiungerlo e poi riprovare", 'danger')
        return redirect(url_for('nuovo_artista'))
    
    if performance_dao.get_performance_by_id_artista(performance_form.get('id_artista')) and not bozza: #l'errore lo segnala il db ma non volevo che ci fosse una segnalazione generica
        flash("Esiste già una performance associata all'artista selezionato", 'danger')
        return redirect(url_for('nuova_performance'))
    
    try:
        ora_inizio = datetime.strptime(f"{performance_form.get('ora_inizio')}", "%H:%M")
        ora_fine = datetime.strptime(f"{performance_form.get('ora_fine')}", "%H:%M")
    except ValueError:
        flash('Il formato dell\'ora non è valido', 'danger')
        return redirect(url_for('nuova_performance'))
    
    giorno_inizio = performance_form.get("giorno_inizio")
    giorno_fine = performance_form.get("giorno_fine")
    if giorno_inizio not in GIORNI_FESTIVAL or giorno_fine not in GIORNI_FESTIVAL:
        flash('Il giorno selezionato non è valido', 'danger')
        return redirect(url_for('nuova_performance'))
    
    index_inizio = ORDINE_GIORNI.index(giorno_inizio)
    index_fine = ORDINE_GIORNI.index(giorno_fine)
    diff_giorni = index_fine - index_inizio
    if diff_giorni<0:
        flash('La data di fine deve essere successiva a quella di inizio', 'danger')
        return redirect(url_for('nuova_performance'))
    if diff_giorni==0 and ora_fine <= ora_inizio:
        flash('L\'orario di fine deve essere successivo a quello di inizio', 'danger')
        return redirect(url_for('nuova_performance'))
    if diff_giorni > 0:
        ora_fine += timedelta(days=diff_giorni)
    durata = ora_fine - ora_inizio
    durata_minuti = durata.total_seconds() / 60
    performance_form['durata']=durata_minuti

    if not others_dao.get_palco_by_id(performance_form.get('id_palco')):
        flash("Il palco selezionato non fa parte del festival", 'danger')
        return redirect(url_for('nuova_performance'))
    
    if not others_dao.get_genere_by_id(performance_form.get('id_genere')):
        flash("Il genere selezionato non fa parte del festival", 'danger')
        return redirect(url_for('nuova_performance'))
    
    if len(performance_form.get('descrizione')) < 50:
        flash('La descrizione deve contenere almeno 50 caratteri', 'danger')
        return redirect(url_for('nuova_performance'))
    
    if performance_form.get('tipo_performance') not in ['0', '1']:
        flash('Bisogna scegliere se pubblicare la performance o tenerla come bozza', 'danger')
        return redirect(url_for('nuova_performance'))
    
    if performance_form['tipo_performance']=='1': #se è definitiva si fanno i controlli di non sovrapposizione
        #modo per uniformare le date per confrontarle
        inizio_nuova = datetime.combine(
            datetime.today() + timedelta(days=index_inizio),
            ora_inizio.time()
        )
        fine_nuova = datetime.combine(
            datetime.today() + timedelta(days=index_fine),
            ora_fine.time()
        )

        performance_esistenti = performance_dao.get_performance(id_palco=performance_form['id_palco'])
        for p in performance_esistenti:
            index_inizio_esistente = ORDINE_GIORNI.index(p['giorno_inizio'])
            index_fine_esistente = ORDINE_GIORNI.index(p['giorno_fine'])

            inizio_esistente = datetime.combine(
                datetime.today() + timedelta(days=index_inizio_esistente),
                datetime.strptime(p['ora_inizio'], "%H:%M").time()
            )
            fine_esistente = datetime.combine(
                datetime.today() + timedelta(days=index_fine_esistente),
                datetime.strptime(p['ora_fine'], "%H:%M").time()
            )

            if (inizio_nuova < fine_esistente) and (fine_nuova > inizio_esistente):
                flash("La performance si sovrappone con un'altra già esistente, si procede quindi a salvarla come bozza", "warning")
                performance_form['tipo_performance'] = '0'
                break
    
    if immagine_copertina and immagine_copertina.filename != "": #rifaccio il controllo perchè se mi trovo in una bozza potrei non avere questi dati disponibii
        try:
            performance_form['immagine_copertina'] = resize_and_save(immagine_copertina, None, FOTO_PERFORMANCE_HEIGHT, f"copertina_{performance_form['id_artista']}")
        except:
            flash('Errore nel salvataggio della copertina', 'danger')
            return redirect(url_for('nuova_performance'))
    else:
        performance_form['immagine_copertina'] = bozza['immagine_copertina']
    
    performance_form['id_organizzatore'] = current_user.id

    performance_form['id_artista'] = int(performance_form['id_artista'])
    performance_form['id_palco'] = int(performance_form['id_palco'])
    performance_form['id_genere'] = int(performance_form['id_genere'])
    performance_form['id_organizzatore'] = int(performance_form['id_organizzatore'])
    performance_form['tipo_performance'] = int(performance_form['tipo_performance'])
    performance_form['durata'] = int(performance_form['durata'])

    #va salvata prima la performance e poi la foto sennò non abbiamo l'id_performance da salvare nel db delle foto
    if id_bozza:
        performance_id = performance_dao.modifica_bozza(int(id_bozza), performance_form)
    else:
        performance_id = performance_dao.aggiungi_performance(performance_form) #non distingue fra bozza e performance...tanto in performance_form is_pubblicata è 0

    if not performance_id:
        if performance_form['tipo_performance'] == 0:
            flash('Errore nel salvataggio della bozza: riprovare', 'danger')
        else:
            flash('Errore nel salvataggio della performance: riprovare', 'danger')
        return redirect(url_for('nuova_performance'))
    else:
        if performance_form['tipo_performance'] == 0:
            flash('Bozza salvata', 'success')
        else:
            flash('Performance salvata', 'success')

    i=0
    for file in request.files.getlist('immagini_extra'):
        i += 1
        if file and file.filename:
            try:
                path = resize_and_save(file, None, FOTO_PERFORMANCE_HEIGHT, f"foto_{i}_{performance_form['id_artista']}")
                others_dao.aggiungi_foto(performance_id, path)
            except Exception as e:
                flash('Errore salvataggio dell\'immagine extra numero {i}', 'warning')
                # essendo facoltative si va avanti

    foto_da_eliminare = []
    for key in request.form:
        if key.startswith("elimina_"):
            foto_da_eliminare.append(request.form[key])
    if foto_da_eliminare:
        i=0
        for id_foto in foto_da_eliminare:
            i+=1
            if not others_dao.elimina_foto(id_foto):
                flash('Errore nella procedura di eliminazione dell\'immagine extra numero {i}', 'warning')

    return redirect(url_for('profilo'))

@app.route('/elimina-bozza/<int:id_bozza>', methods=['POST'])
@login_required
def elimina_bozza(id_bozza):
    if check_partecipante():
        flash("Solo chi è registrato come organizzatore può operare sulle performance", "danger")
        return redirect(url_for('home'))
    
    bozza = performance_dao.get_bozza_by_id(id_bozza)

    if not bozza or bozza['id_organizzatore'] != current_user.id or bozza['is_pubblicata'] != 0:
        flash("Bozza non trovata o accesso non autorizzato", "danger")
        return redirect(url_for('profilo'))

    if not others_dao.elimina_foto_by_id_performance(id_bozza):
        flash("Errore nell'eliminazione delle immagini extra", "warning")

    if performance_dao.elimina_bozza(id_bozza):
        flash("Bozza eliminata con successo", "success")
    else:
        flash("Errore durante l'eliminazione della bozza", "danger")

    return redirect(url_for('profilo'))

@app.route('/nuovo-artista')
@login_required
def nuovo_artista():
    if check_partecipante():
        flash("Solo chi è registrato come organizzatore può aggiungere un nuovo artista", "danger")
        return redirect(url_for('home'))
    return render_template('new_artista.html')

@app.route('/nuovo-artista', methods=['POST'])
@login_required
def nuovo_artista_post():
    if check_partecipante():
        flash("Solo chi è registrato come organizzatore può aggiungere un nuovo artista", "danger")
        return redirect(url_for('home'))
    
    artista_form = request.form.to_dict()
    if not artista_form.get('nome'):
        flash('Nome dell\'artista mancante', 'danger')
        return redirect(url_for('nuovo_artista'))
    
    artista_esistente = others_dao.get_artista_by_nome(artista_form.get('nome'))
    if artista_esistente:
        flash(f"{artista_form.get('nome')} è già presente nel database", 'danger')
        return redirect(url_for('nuovo_artista'))

    biografia = artista_form.get("biografia")
    artista_form['biografia'] = biografia if biografia else None #piuttosto che avere la stringa vuota

    foto_profilo = request.files.get("foto_profilo")
    if foto_profilo and foto_profilo.filename:
        try:
            artista_form['foto_profilo'] = resize_and_save(foto_profilo, None, FOTO_PROFILO_HEIGHT, f"profilo_{artista_form['nome']}")
        except:
            flash('Errore nel salvataggio della copertina', 'warning')
            artista_form['foto_profilo'] = None
    else:
        artista_form['foto_profilo'] = None

    next_page = artista_form.pop('next', None)
    if not next_page or not next_page.endswith(url_for('nuova_performance')):
        next_page = url_for('profilo')

    success = others_dao.aggiungi_artista(artista_form)

    if success:
        flash('Artista registrato', 'success')
        return redirect(next_page)
    else:
        flash('Errore nella procedura di registrazione dell\'artista: riprovare', 'danger')
        return redirect(url_for('nuovo_artista'))

#registrazione

@app.route('/registrati')
def registrati():
    return render_template('registrazione.html')

@app.route('/registrati', methods=['POST'])
def registrati_post():
    nuovo_utente_form = request.form.to_dict()

    campi_necessari = ['nome', 'cognome', 'email', 'password', 'tipo_utente']
    if any(not nuovo_utente_form.get(campo) for campo in campi_necessari):
        flash('Non sono stati compilati tutti i campi della registrazione', 'danger')
        return redirect(url_for('registrati'))
    
    if nuovo_utente_form.get('tipo_utente') not in ['0', '1']:
        flash('Ruolo non valido', 'danger')
        return redirect(url_for('registrati'))
    
    if len(nuovo_utente_form.get('password')) < 8:
        flash('La password deve essere di almeno 8 caratteri', 'danger')
        return redirect(url_for('registrati'))
    
    if not is_email(nuovo_utente_form.get('email')):
        flash('Email non valida', 'danger')
        return redirect(url_for('registrati'))

    if utenti_dao.get_user_by_email(nuovo_utente_form.get('email')):
        flash('C\'è già un utente registrato con questa mail', 'danger')
        return redirect(url_for('registrati'))
    
    nuovo_utente_form['password'] = generate_password_hash(nuovo_utente_form.get('password'))
    nuovo_utente_form['tipo_utente'] = int(nuovo_utente_form['tipo_utente'])

    success = utenti_dao.aggiungi_utente(nuovo_utente_form)

    if success:
        flash('Registrazione effettuata con successo, effettua il login per accedere al profilo appena creato', 'success')
        return redirect(url_for('home'))
    else:
        flash('Errore nella registrazione: riprovare', 'danger')
        return redirect(url_for('registrati'))

#login e gestione utente

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    utente_form = request.form.to_dict()
    utente_db = utenti_dao.get_user_by_email(utente_form.get('email'))

    if not utente_db or not check_password_hash(utente_db['password'], utente_form.get('password')):
        flash('Login non riuscito: la mail o la password non sono corrette!', 'danger')
        return redirect(url_for('home'))
    
    utente = User(id=utente_db['id'], email=utente_db['email'], password=utente_db['password'], nome=utente_db['nome'], cognome=utente_db['cognome'], is_partecipante=utente_db['is_partecipante'])
    login_user(utente, True)

    if utente.is_partecipante == 1:
        messaggio = "Puoi acquistare i biglietti per il festival andando sulla pagina dei biglietti"
    else:
        messaggio = "Puoi creare gestire e creare performance andando sulla pagina profilo"
    
    flash('Ciao ' + utente_db['nome']+'! ' + messaggio, 'success')
    return redirect(url_for('home'))

@login_manager.user_loader
def load_user(utente_id):
    utente_db = utenti_dao.get_user_by_id(utente_id)
    if utente_db is not None:
        return User(id=utente_db['id'], email=utente_db['email'], password=utente_db['password'], nome=utente_db['nome'], cognome=utente_db['cognome'], is_partecipante=utente_db['is_partecipante'])
    return None


#generiche funzioni ricorrenti
def check_partecipante():
    if not current_user.is_authenticated or not current_user.is_partecipante:
        return False
    return True

def ha_gia_biglietto():
    return acquisti_biglietti_dao.get_biglietto_by_id_utente(current_user.id) is not None

def giorni_to_bin_str(opzione):
    return ''.join(str(opzione[giorno]) for giorno in ORDINE_GIORNI)

def is_email(val):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, val) is not None

def resize_and_save(img_file, target_width, target_height, prefix):
    img = Image.open(img_file)
    w, h = img.size
    new_w = int(w / h * target_height)
    img.thumbnail((new_w, target_height), Image.Resampling.LANCZOS)
    ext = img_file.filename.rsplit('.', 1)[-1].lower()
    filename = secure_filename(f"{prefix}_{int(time.time())}.{ext}")
    path = f"static/images/{filename}"
    img.save(path)
    return f"images/{filename}"