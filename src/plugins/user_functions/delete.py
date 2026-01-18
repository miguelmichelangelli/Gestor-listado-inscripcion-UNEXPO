from plugins.delete_student import delete_student

def delete(sql):
    exp = int(input("Enter student expedient number to delete: "))
    delete_student(sql, exp)