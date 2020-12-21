# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 22:46:52 2020

@author: Alfonso Chacon Roldan
"""
import sys
sys.path.append('D:\Github\Horarios')

import tkinter as tk
from tkinter import filedialog
import horarios as hr
import os
import pandas as pd

root = tk.Tk()
# root.withdraw()
root.geometry("570x500")
root.title("Verificador y Exportador de Pizarras")

text = tk.Text(font=("Helvetica 10"))
greeting = "Este programa toma el horario de un instituto en excel y una tabla de excel incluyendo todos los profesoress.\
 La lista de profesores debe incluir una fila por profesor, y los nombres asociados \ncon ese educador separados en las columnas."
text.insert(tk.INSERT, greeting)
text.place(x=0, y=0, height=57)

school_name_label = tk.Label(root, text="Nombre del colegio")
school_name_label.place(x=0,y=60)
school_name_entry = tk.Entry(root, width=40, borderwidth=3)
school_name_entry.place(x=120,y=60)

schedule_path_label = tk.Label(root, text="Pizarra del instituto")
schedule_path_label.place(x=0, y=90)
schedule_path_entry = tk.Entry(root, width=65, borderwidth=3)
schedule_path_entry.place(x=120, y=90)

num_periods_label = tk.Label(root, text="Máximo número de clases en un día")
num_periods_label.place(x=0, y=120)
num_periods_entry = tk.Entry(root, width=5, borderwidth=3)
num_periods_entry.place(x=200, y=120)

teachers_path_label = tk.Label(root, text="Lista de educadores")
teachers_path_label.place(x=0, y=160)
teachers_path_entry = tk.Entry(root, width=65, borderwidth=3)
teachers_path_entry.place(x=120, y=160)


def select_schedule():
    global schedule
    global schedule_dir
    schedule_path = filedialog.askopenfilename(
        parent=root,
        title='Choose file',
        filetypes=[('Excel file', '.xlsx')]
        )
    schedule_path_entry.delete(0, 'end')
    schedule_path_entry.insert(0,schedule_path)
    schedule = pd.read_excel(schedule_path)
    schedule.rename(columns={'Unnamed: 0': 'Dia/Hora'}, inplace=True)
    schedule.set_index("Dia/Hora", inplace=True)
    schedule_dir = os.path.dirname(schedule_path)
    print(schedule_dir)

def set_school_name():
    global school_name
    school_name = str(school_name_entry.get())
    print(school_name)
       
def select_teachers():
    global raw_teachers
    teachers_path = filedialog.askopenfilename(
        parent=root,
        title='Choose file',
        filetypes=[('Excel file', '.xlsx')]
        )
    teachers_path_entry.delete(0, 'end')
    teachers_path_entry.insert(0,teachers_path)
    raw_teachers = pd.read_excel(teachers_path)
    
def set_max_periods():
    global max_num_periods
    max_num_periods = int(num_periods_entry.get())
    print(max_num_periods)
    
def process_schedule(button):
    global curr_school
    curr_school = hr.School(school_name,schedule,raw_teachers, max_num_periods, schedule_dir)
    curr_school.process_and_save_teacher_schedules()
    curr_school.process_and_save_groups_schedules()
    if curr_school.missing_subjects.size > 0:
        # miss_subjects_text = tk.Text(fg="red", font=("Helvetica 10"))
        missing_subjects= "Atención: Estas clases no están asociadas con un educador: \n" + ", ".join(map(str,curr_school.missing_subjects))
        miss_subjects_label = tk.Label(root, text=missing_subjects, fg="red", justify=tk.LEFT, wraplength=500)
        miss_subjects_label.place(x=0, y=260)
        miss_subjects_label.update()
        print(miss_subjects_label.winfo_height())
    curr_school.check_and_print_unused_names()
    if len(curr_school.all_unused_names) > 0:
        all_unused_names = "Atención: Los siguientes nombres de profesores no están siendo utilizados: \n" + curr_school.all_unused_names
        all_unused_label = tk.Label(root, text=all_unused_names, fg="blue", justify=tk.LEFT, wraplength=500)
        all_unused_label.place(x=0, y=(260 + miss_subjects_label.winfo_height() ))
        all_unused_label.update()
        print(all_unused_label.winfo_height(), all_unused_label.winfo_y())
    if all_unused_label.winfo_height() > 1:
        reminder_label = tk.Label(root, text="Recuerde que los choques no consideran los valores mencionados arriba.", font="Helvetica 10 bold")
        reminder_label.place(x=0, y=all_unused_label.winfo_y() + all_unused_label.winfo_height())
        reminder_label.update()
    curr_school.check_and_print_conflicts()
    if len(curr_school.all_conflicts) > 0:
        all_conflicts = "Choques: \n" + curr_school.all_conflicts
        all_conflicts_label = tk.Label(root, text=all_conflicts, fg="red", justify=tk.LEFT, wraplength=500)
        all_conflicts_label.place(x=0, y=(reminder_label.winfo_y() + reminder_label.winfo_height() ))
        all_conflicts_label.update()
    

b1 = tk.Button(root, text='Guardar', command=set_school_name)
b1.place(x=370, y=58)

b2 = tk.Button(root, text='Abrir', command=select_schedule)
b2.place(x=520, y=88)

b3 = tk.Button(root, text='Guardar', command=set_max_periods)
b3.place(x=240, y=118)

b4 = tk.Button(root, text='Abrir', command=select_teachers)
b4.place(x=520, y=158)

b5 = tk.Button(root, text='Procesar horario', command=lambda: process_schedule(b5), padx=50, pady=8, borderwidth=7)
b5.place(relx=0.5, rely=0.44, anchor=tk.CENTER)


root.mainloop()