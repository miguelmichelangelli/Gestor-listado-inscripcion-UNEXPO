def create_db(sql):
    """ 
    Crea un archivo de SQLite en caso de que no exista.
    """
    conn = sql.connect('unexpo.db')
    conn.commit()
    conn.close()
    print("Base de datos creada exitosamente.")