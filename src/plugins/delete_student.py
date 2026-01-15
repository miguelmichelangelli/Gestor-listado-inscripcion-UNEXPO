def delete_student(sql, exp):
    conn = sql.connect('unexpo.db')
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM unexpo WHERE expediente = ?", (exp, )
    )

    conn.commit()
    conn.close()