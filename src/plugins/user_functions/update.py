from plugins.update_student import update_student

def update(sql):
    exp = int(input("Enter student expedient number to update: "))
    
    print("Enter new detailsa, if not applicable enter the same value:")

    new_day = input("New day: ")
    new_hour = input("New hour: ")
    new_turn = int(input("New turn: "))
    new_semester = int(input("New semester: "))
    new_performance_index = float(input("New performance index: "))
    new_academic_index = float(input("New academic index: "))
    update_student(sql, (new_day, new_hour, new_turn, new_semester, new_performance_index, new_academic_index, exp))