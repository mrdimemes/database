# database
Simple self-made database to track the time spent on self-education. Writed in python 3.8.

----------------
# Functional
Time counting;  
Storage and processing of time and task data;  
Data visualization.

----------------
# Need libraries
datetime  
logging  
math  
re  
random  
matplotlib  
numpy  
pandas  

----------------
Data stored in .csv-files and processing using pandas by 4 classes:  
DataBase from run_database.py;  
DataProcessor from data_processor.py;  
TimeCounter from time_counter.py;  
Visualizer from visualizer.py.  

Main class is DataBase, other classes are impurity. These classes do not work on their own.

DataBase processing user input in text command format by DataBase.input_processing function. Other function in
DataBase are user-command functions using DataProcessor, TimeCounter and Visualizer code.

codes.csv signature:  
Columns: «task» (task name), «code» and «priority» (number).  

time.csv signature: 
Columns: «date» (dd-mm-yy format), «tasks» (codes with space separation), «ratios» (with space separation) and «total».  
Rows appends by /add command.  

Data presentation format - tree-graph of tasks. Graph structure information is contained in codes.csv (column "code").
Codes have the form "X_Y_Z", where X, Y and Z defines the «path» to the corresponding graph node.
Column "priority" in codes.csv determines the importance of task for user (for recommendation).

File time.csv contain information about user activity in its rows.  

Run run_database.py to get started (thx cap). All files must be in one dir.

----------------
Have some fun ~