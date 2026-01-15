def update_student(sql, data):
    conn = sql.connect('unexpo.db')
    cursor = conn.cursor()

    cursor.execute(
        """UPDATE unexpo SET dia = ? WHERE expediente = ?""", data
    )

    conn.commit()
    conn.close()