def select_student_by_exp(sql, exp):
    conn = sql.connect('unexpo.db')
    cursor = conn.cursor()

    cursor.execute(
        """SELECT * FROM unexpo WHERE expediente = ?""", (exp,)
    )

    data = cursor.fetchall()

    conn.commit()
    conn.close()

    return data