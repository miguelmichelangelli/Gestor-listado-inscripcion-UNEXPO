def create_table(sql):
    """ 
    Crea una tabla en el archivo SQL
    """

    conn = sql.connect('unexpo.db')
    cursor = conn.cursor()

    cursor.execute(
        """CREATE TABLE unexpo (
            expediente int,
            dia string,
            hora string,
            turno int,
            semestre int,
            rendimiento float,
            academico float
        )"""
    )

    conn.commit()
    conn.close()

