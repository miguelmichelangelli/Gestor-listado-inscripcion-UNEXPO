from plugins.select_student_by_exp import select_student_by_exp

def select(sql):
    exp = int(input("Enter student expedient number to select: "))
    student = select_student_by_exp(sql, exp)
    return student