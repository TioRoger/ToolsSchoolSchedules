# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 16:53:11 2020

@author: alfon
"""

import pandas as pd
import xlsxwriter

# We start by defining some classes
days_short = ["Lu","Ma","Mi","Ju","Vi"]
days_long = ["Lunes", "Martes","Miercoles", "Jueves", "Viernes"]

class Teacher:
    def __init__(self,name, subject, pseudos):
            self.name = name
            self.subject = subject
            self.pseudos = pseudos
            self.rawschedule = ""
            self.vertschedule = ""
            self.finalschedule = ""
            self.conflicts = ""
            self.unusedpseudos = ""
    def pseudonyms(self):
        print("Pseudónimos: " + ', '.join(map(str,self.pseudos)))
        
    def raw_schedule(self, schedule):
        teacher_schedule = schedule.unstack()[schedule.unstack().isin(self.pseudos)].reset_index()
        teacher_schedule.rename(columns={'level_0': 'Seccion', 0:"Asignatura"}, inplace=True)
        self.schedule = teacher_schedule
        return teacher_schedule
    def get_conflicts(self):
        if isinstance(self.rawschedule, pd.DataFrame):
            return list(self.schedule["Dia/Hora"].value_counts().index[self.schedule["Dia/Hora"].value_counts()>1])
        else:
            print("Schedule is empty.\n")      
    def clean_duplicates_from_schedule(self):
        if isinstance(self.rawschedule, pd.DataFrame):
            vertschedule = self.rawschedule.copy()
            vertschedule["Seccion"]=vertschedule.groupby(["Dia/Hora"])["Seccion"].transform(lambda x: ', '.join(x))
            return vertschedule.drop_duplicates(subset=['Dia/Hora'])
        else:
            print("Schedule is empty.\n")
    def create_final_schedule(self, template):
        if isinstance(self.vertschedule, pd.DataFrame):
            final_schedule = pd.merge(template,self.vertschedule,on='Dia/Hora',how='left')
            day_period = final_schedule["Dia/Hora"].str.split("-",n=1,expand=True)
            final_schedule["Day"] = day_period[0]
            final_schedule["Period"] = pd.to_numeric(day_period[1])
            final_schedule = final_schedule[["Seccion","Day","Period"]].pivot(index="Period",columns='Day', values='Seccion' )
            return final_schedule[["Lu","Ma","Mi","Ju","Vi"]]
        else:
            print("Vertical Schedule is empty.\n")
    def save_schedule(self, writer):
        if isinstance(self.finalschedule, pd.DataFrame):
            self.finalschedule.to_excel(writer,self.name)
        else:
            print("Final schedule is empty.\n")
    def check_nickname_usage(self, school):
        return self.pseudos[~pd.Series(self.pseudos).isin(school.all_subjects)]
            

class Classgroup:
    def __init__(self, name):
        self.name = name
        self.schedule = ""
    def group_schedule(self, schedule):
        schedule = pd.DataFrame(schedule[self.name]).reset_index()
        day_period = schedule["Dia/Hora"].str.split("-",n=1,expand=True)
        schedule["Day"] = day_period[0]
        schedule["Period"] = pd.to_numeric(day_period[1])
        schedule.rename(columns={self.name: 'Asignatura'}, inplace=True)
        schedule = schedule[["Asignatura","Day","Period"]].pivot(index="Period",columns='Day', values='Asignatura' )
        return schedule[["Lu","Ma","Mi","Ju","Vi"]]
    def save_schedule(self, writer):
        if isinstance(self.schedule, pd.DataFrame):
            self.schedule.to_excel(writer,self.name)
        else:
            print("Group schedule is empty.\n")

class School:
    def __init__(self,name,schedule,raw_teachers, num_periods, dir_path):
        self.name = name
        self.schedule = schedule
        self.raw_teachers = raw_teachers
        self.dir_path = dir_path
        self.num_periods = num_periods
        self.all_unused_names = ""
        self.all_conflicts = ""
        self.all_periods = [day+"-"+str(period+1) for day in days_short for period in range(self.num_periods)]
        self.vertical_schedule = self.schedule.unstack()
        self.all_subjects = pd.Series(pd.unique(self.vertical_schedule))
        self.all_teachers_names = pd.Series(pd.unique(
        self.raw_teachers.set_index("Nombre")[raw_teachers.set_index("Nombre").columns[1:]].unstack()))
        self.missing_subjects = self.all_subjects[~self.all_subjects.isin(self.all_teachers_names)]
        self.teachers = [Teacher(teach.Nombre,teach.Asignatura, self.raw_teachers.iloc[teach[0]][2:].dropna().values) 
            for teach in self.raw_teachers.itertuples()]
        self.template = pd.DataFrame(list(zip(self.all_periods)), columns=["Dia/Hora"])
        self.groups = [Classgroup(group) for group in schedule.columns]
        self.profs_writer = pd.ExcelWriter(self.dir_path + "/" + self.name.replace(" ","") + '_profes.xlsx', engine='xlsxwriter')
        self.class_writer = pd.ExcelWriter(self.dir_path + "/" + self.name.replace(" ","") + '_secciones.xlsx', engine='xlsxwriter')   
    def process_and_save_teacher_schedules(self):
        for teacher in self.teachers:
            teacher.rawschedule = teacher.raw_schedule(self.schedule)
            teacher.conflicts = teacher.get_conflicts()
            teacher.unusedpseudos = teacher.check_nickname_usage(self)
            teacher.vertschedule =  teacher.clean_duplicates_from_schedule()
            teacher.finalschedule = teacher.create_final_schedule(self.template)
            teacher.save_schedule(self.profs_writer)
        self.profs_writer.save()
    def process_and_save_groups_schedules(self):
        for group in self.groups:
            group.schedule = group.group_schedule(self.schedule)
            group.save_schedule(self.class_writer)
        self.class_writer.save()
    def check_and_print_conflicts(self):
        for teacher in self.teachers:
            if len(teacher.conflicts) > 0:
                conflicts = teacher.vertschedule[teacher.vertschedule["Dia/Hora"].isin(teacher.conflicts)]
                print(conflicts.columns)
                self.all_conflicts = self.all_conflicts + "Educador: " + teacher.name + ", dia y hora: " + ", ".join(map(str,conflicts["Dia/Hora"])) + ", secciones: " + ", ".join(map(str,conflicts["Seccion"])) + "\n"
                # print(teacher.vertschedule[teacher.vertschedule["Dia/Hora"].isin(teacher.conflicts)])
    def check_and_print_unused_names(self):
        for teacher in self.teachers:
            if teacher.unusedpseudos.size > 0:
                self.all_unused_names = self.all_unused_names + "Educador: " + str(teacher.name) + ", nombres:" + str(teacher.unusedpseudos) + "\n"
                