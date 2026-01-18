from plugins.add_student import add_student

def add(sql):
    exp = input("Enter student expedient number: ")
    day = input("Enter day of the week: ")
    time = input("Enter time (HH:MM): ")
    turn = int(input("Enter turn number: "))
    semester = int(input("Enter semester: "))
    academic_index = float(input("Enter academic index: "))
    academic_performance = float(input("Enter academic performance: "))

    add_student(sql, (exp, day, time, turn, semester, academic_index, academic_performance))