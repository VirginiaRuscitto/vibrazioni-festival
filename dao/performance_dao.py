import sqlite3

def aggiungi_performance(performance):

    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = '''
        INSERT INTO performance(
            id_artista, 
            id_organizzatore, 
            id_palco, 
            id_genere, 
            giorno_inizio, 
            ora_inizio, 
            giorno_fine, 
            ora_fine, 
            immagine_copertina, 
            is_pubblicata,
            durata,
            descrizione
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    try:
        cursor.execute(sql, (
            performance['id_artista'],
            performance['id_organizzatore'],
            performance['id_palco'],
            performance['id_genere'],
            performance['giorno_inizio'],
            performance['ora_inizio'],
            performance['giorno_fine'],
            performance['ora_fine'],
            performance['immagine_copertina'],
            performance['tipo_performance'],
            performance['durata'],
            performance['descrizione']
        ))
        conn.commit()
        nuovo_id = cursor.lastrowid
    except Exception as e:
        print('ERROR', str(e))
        conn.rollback()
        nuovo_id = None

    cursor.close()
    conn.close()

    return nuovo_id

def get_performance(giorno=None, id_genere=None, id_palco=None):
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = '''
        SELECT 
            performance.*, 
            artisti.nome AS nome_artista,
            artisti.foto_profilo,
            artisti.biografia,
            generi.nome AS nome_genere,
            palchi.nome AS nome_palco,
            palchi.id
        FROM performance
        JOIN artisti ON performance.id_artista = artisti.id
        JOIN generi ON performance.id_genere = generi.id
        JOIN palchi ON performance.id_palco = palchi.id
        WHERE performance.is_pubblicata = 1
    '''

    params = []

    if giorno:
        sql += ' AND performance.giorno_inizio = ?'
        params.append(giorno)
    if id_genere:
        sql += ' AND performance.id_genere = ?'
        params.append(id_genere)
    if id_palco:
        sql += ' AND performance.id_palco = ?'
        params.append(id_palco)

    sql += '''
        ORDER BY 
            CASE giorno_inizio
                WHEN 'venerdi' THEN 1
                WHEN 'sabato' THEN 2
                WHEN 'domenica' THEN 3
            END,
            ora_inizio ASC,
            palchi.id ASC
        '''

    cursor.execute(sql, params)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows

def get_performance_by_id(id):
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = '''
        SELECT 
            performance.*, 
            artisti.nome AS nome_artista,
            artisti.foto_profilo,
            artisti.biografia,
            generi.nome AS nome_genere,
            palchi.nome AS nome_palco
        FROM performance
        JOIN artisti ON performance.id_artista = artisti.id
        JOIN generi ON performance.id_genere = generi.id
        JOIN palchi ON performance.id_palco = palchi.id
        WHERE performance.is_pubblicata = 1 AND performance.id = ?
    '''

    cursor.execute(sql, (id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result

def get_performance_by_id_artista(id):
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = "SELECT * FROM performance WHERE performance.is_pubblicata = 1 AND id_artista = ?"

    cursor.execute(sql, (id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result


def get_id_performance():
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = "SELECT id FROM performance WHERE performance.is_pubblicata = 1"

    cursor.execute(sql)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows

def get_bozze_by_organizzatore(id_organizzatore):
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = '''
        SELECT 
            performance.*, 
            artisti.nome AS nome_artista
        FROM performance
        JOIN artisti ON performance.id_artista = artisti.id
        WHERE id_organizzatore = ?
          AND is_pubblicata = 0
        ORDER BY 
            CASE giorno_inizio
                WHEN 'venerdi' THEN 1
                WHEN 'sabato' THEN 2
                WHEN 'domenica' THEN 3
            END,
            ora_inizio ASC
    '''

    cursor.execute(sql, (id_organizzatore,))
    bozze = cursor.fetchall()

    cursor.close()
    conn.close()

    return bozze

def get_bozza_by_id(id):
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = '''
        SELECT 
            performance.*, 
            artisti.nome AS nome_artista,
            artisti.foto_profilo,
            artisti.biografia,
            generi.nome AS nome_genere,
            palchi.nome AS nome_palco
        FROM performance
        JOIN artisti ON performance.id_artista = artisti.id
        JOIN generi ON performance.id_genere = generi.id
        JOIN palchi ON performance.id_palco = palchi.id
        WHERE performance.is_pubblicata = 0 AND performance.id = ?
    '''

    cursor.execute(sql, (id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result

def modifica_bozza(id_bozza, dati):
    conn = sqlite3.connect('db/festival.db')
    cursor = conn.cursor()

    sql = '''
        UPDATE performance SET
            id_artista = ?,
            giorno_inizio = ?,
            ora_inizio = ?,
            giorno_fine = ?,
            ora_fine = ?,
            id_palco = ?,
            id_genere = ?,
            descrizione = ?,
            is_pubblicata = ?,
            immagine_copertina = ?,
            durata = ?
        WHERE id = ?
    '''

    valori = (
        dati['id_artista'],
        dati['giorno_inizio'],
        dati['ora_inizio'],
        dati['giorno_fine'],
        dati['ora_fine'],
        dati['id_palco'],
        dati['id_genere'],
        dati['descrizione'],
        dati['tipo_performance'],
        dati['immagine_copertina'],
        dati['durata'],
        id_bozza
    )

    try:
        cursor.execute(sql, valori)
        conn.commit()
    except Exception as e:
        print('ERROR', str(e))
        conn.rollback()
        id_bozza = None

    cursor.close()
    conn.close()

    return id_bozza

def elimina_bozza(id_bozza):
    conn = sqlite3.connect('db/festival.db')
    cursor = conn.cursor()

    success = False
    sql = "DELETE FROM performance WHERE id = ? AND is_pubblicata = 0"

    try:
        cursor.execute(sql, (id_bozza,))
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def get_id_artisti_occupati():
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = "SELECT id_artista FROM performance WHERE is_pubblicata = 1"

    cursor.execute(sql)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [row['id_artista'] for row in rows]