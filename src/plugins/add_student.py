def add_student(sql, student_data):
    """
    Añade un estudiante a la base de datos
    """

    conn = sql.connect('unexpo.db')
    cursor = conn.cursor()

    cursor.execute(
        # """INSERT INTO unexpo VALUES (expediente, dia, hora, turno, semestre,
        # rendimiento, academico) """
        """ INSERT INTO unexpo VALUES (?, ?, ?, ?, ?, ?, ?) """, student_data
    )

    conn.commit()
    conn.close()