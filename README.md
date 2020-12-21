# ToolsSchoolSchedules
Tools to help in the process of creating a school schedule
A person close to me offers the service of creating schedule's for schools at the end of the year. 
While there are tools in the market for these, the approach is very traditional. This has the advantage of
flexibility, which is very important for a lot of these schools, due to the lack of resources, and specially 
for the teachers, as they might work at different schools and therefore have special needs. 

The biggest issue is colliding hours, when a teacher is booked at the same time for two different groups. 
This is the main purpose of the program. The schedule to check is a table with days/hours as rows and the different
groups as columns. Some teachers have more than one subject, each has a unique identifier and all are contained
in a table with teachers as rows and each unique identifier in its own cell. 

The application takes both of these tables and verifies values in one missing in the other, since these might be
conflicts that the application wouldn't identify. It then checks for conflicts for each teacher, and saves their
own schedule to an excel sheet. Afterwards it saves the schedule for each group to a new sheet in a different
excel file. 

horarios.py contains the classes defined to process the tables. 

AppHorarios.py is the script creating the gui for the application using tkinter.
