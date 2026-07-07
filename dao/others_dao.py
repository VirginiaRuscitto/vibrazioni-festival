import sqlite3

#artisti
def get_artisti():
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM artisti ORDER BY nome ASC'
    cursor.execute(sql)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows

def aggiungi_artista(artista):
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'INSERT INTO artisti (nome, foto_profilo, biografia) VALUES (?, ?, ?)'

    try: 
        cursor.execute(sql, (artista['nome'], artista['foto_profilo'], artista['biografia']))
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def get_artista_by_id(id):
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM artisti WHERE id = ?'
    cursor.execute(sql, (id,))
    artista = cursor.fetchone()

    cursor.close()
    conn.close()

    return artista

def get_artista_by_nome(nome):
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM artisti WHERE nome = ?'
    cursor.execute(sql, (nome,))
    artista = cursor.fetchone()

    cursor.close()
    conn.close()

    return artista

#palchi
def get_palchi():
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM palchi ORDER BY nome ASC'
    cursor.execute(sql)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows

def get_palco_by_id(id):
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM palchi WHERE id = ?'
    cursor.execute(sql, (id,))
    palco = cursor.fetchone()

    cursor.close()
    conn.close()

    return palco

#generi
def get_generi():
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM generi ORDER BY nome ASC'
    cursor.execute(sql)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows

def get_genere_by_id(id):
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM generi WHERE id = ?'
    cursor.execute(sql, (id,))
    genere = cursor.fetchone()

    cursor.close()
    conn.close()

    return genere

#foto_performance
def aggiungi_foto(id, nome):
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'INSERT INTO foto_performance (id_performance, foto) VALUES (?, ?)'

    try: 
        cursor.execute(sql, (id, nome))
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    return success


def get_foto_by_performance(id_performance):
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = "SELECT * FROM foto_performance WHERE id_performance = ?"

    cursor.execute(sql, (id_performance,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows

def get_foto_by_id(id):
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = "SELECT * FROM foto_performance WHERE id = ?"

    cursor.execute(sql, (id,))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return row

def elimina_foto(id_foto):
    conn = sqlite3.connect('db/festival.db')
    cursor = conn.cursor()

    success = False
    sql = "DELETE FROM foto_performance WHERE id = ?"
    try: 
        cursor.execute(sql, (id_foto,))
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        conn.rollback()

    cursor.close()
    conn.close()
    return success

def elimina_foto_by_id_performance(id):
    conn = sqlite3.connect('db/festival.db')
    cursor = conn.cursor()

    success = False
    sql = "DELETE FROM foto_performance WHERE id_performance = ?"
    try: 
        cursor.execute(sql, (id,))
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        conn.rollback()

    cursor.close()
    conn.close()
    return success