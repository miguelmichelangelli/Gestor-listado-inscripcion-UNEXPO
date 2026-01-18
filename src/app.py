import sqlite3 as sql
from plugins.create_db import create_db
from plugins.create_table import create_table
from plugins.add_student import add_student
from plugins.select_student_by_exp import select_student_by_exp
from plugins.update_student import update_student
from plugins.delete_student import delete_student

from plugins.user_functions.add import add
from plugins.user_functions.delete import delete
from plugins.user_functions.select import select
from plugins.user_functions.update import update

# create_db(sql)

# create_table(sql)

# add_student(sql, (2022103301, 'Lunes', '8:45', 92, 8, 7.00, 0.88))

# student = select_student_by_exp(sql, 2019203058)
# print(student)

# update_student(sql, ('Martes', 2019203058))

# delete_student(sql, 2019203058)

# add(sql)
# delete(sql)
# print(select(sql))

update(sql)