import sqlite3

def get_biglietto_by_id_utente(id):
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM acquisti_biglietti WHERE id_utente = ?'
    cursor.execute(sql, (id,))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return row

def acquista_biglietto(id_biglietto, id_utente, data_acquisto, ora_acquisto):
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    success = False
    sql = 'INSERT INTO acquisti_biglietti(id_biglietto, id_utente, data_acquisto, ora_acquisto) VALUES(?,?,?,?)'
    
    try:
        cursor.execute(sql, (id_biglietto, id_utente, data_acquisto, ora_acquisto))
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    return success


def conta_biglietti_venduti(giorno):
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    giorno = giorno.lower()
    if giorno not in ['venerdi', 'sabato', 'domenica']:
        return None

    sql = f"SELECT COUNT(*) as totale FROM acquisti_biglietti ab JOIN biglietti b ON ab.id_biglietto = b.id WHERE b.{giorno} = 1"
    cursor.execute(sql)
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return row['totale']