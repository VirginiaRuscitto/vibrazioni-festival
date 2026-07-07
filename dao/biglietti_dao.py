import sqlite3

def trova_id_biglietto(nome, venerdi, sabato, domenica):
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT id FROM biglietti WHERE nome = ? AND venerdi = ? AND sabato = ? AND domenica = ?'
    cursor.execute(sql, (nome, venerdi, sabato, domenica))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return row
    
def get_biglietti():
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM biglietti'
    cursor.execute(sql)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows

def get_biglietti_distinti():
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT nome, MAX(descrizione) AS descrizione, MAX(nome_visualizzato) AS nome_visualizzato FROM biglietti GROUP BY nome ORDER BY MIN(id) ASC'
    cursor.execute(sql)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows

def get_biglietti_by_nome(nome):
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM biglietti WHERE nome = ? ORDER BY id ASC'
    cursor.execute(sql, (nome,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows

def get_biglietto_by_id(id):
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM biglietti WHERE id = ?'
    cursor.execute(sql, (id,))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row:
        return row
    else:
        return None