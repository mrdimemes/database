import datetime as dt
import re

import numpy as np
import pandas as pd


class DataProcessor():
    '''
    impurity class for working with data.
    Need datetime as dt; re; numpy as np; pandas as pd.
    '''
    def load_data(self, preprocessing=True):
        '''
        Load data from .csv as pandas.DataFrame objects and
        set it as attributes.
        preprocessing flad for time_df preprocessing
        (False for raw .csv reading (faster))
        '''
        self.time_df = pd.read_csv(self.path + 'time.csv')
        self.codes_df = pd.read_csv(self.path + 'codes.csv')
        if preprocessing:
            self.time_df_preprocessing(direction='forward')
        
    def save_data(self, preprocessing=True):
        '''
        Save self.time_df, self.codes_df pandas.DataFrame objects to .csv
        and delete from DataProcessor obj.
        '''
        if preprocessing:
            self.time_df_preprocessing(direction='backward')
            self.time_df.to_csv(self.path + 'time.csv')
        else:
            self.time_df.to_csv(self.path + 'time.csv', index=False)
        self.codes_df.to_csv(self.path + 'codes.csv', index=False)
        self.close_data()
        
    def close_data(self):
        del self.time_df
        del self.codes_df
        
    def time_df_preprocessing(self, direction):
        '''
        If direction is "forward":
        Set date column of of self.time pandas.DataFrame as
        datetime index;
        Fill missing days of self.time_df;
        Convert self.time_df columns elements from strings 
        to tuples.
        
        If direction is "backward":
        Convert self.time_df columns elements from tuples 
        to strings.
        
        Incorrect derection raise ValueError.
        '''
        if direction == 'forward':
            self.time_df.date = pd.to_datetime(self.time_df.date)
            self.time_df = self.time_df.set_index('date')
            self.time_df = self.time_df.asfreq('1d').fillna(
                value={'tasks':'0', 'ratios':'1.0', 'total':0})
            
            column_list = []

            for string in self.time_df.tasks:
                tuple_of_codes = tuple(string.split())
                column_list.append(tuple_of_codes)

            self.time_df.tasks = column_list
            column_list = []

            for string in self.time_df.ratios:
                tuple_of_ratios = tuple(map(float, string.split()))
                column_list.append(tuple_of_ratios)

            self.time_df.ratios = column_list
            
        elif direction == 'backward':
            column_list = []

            for tuple_of_codes in self.time_df.tasks:
                string = ' '.join(tuple_of_codes)
                column_list.append(string)

            self.time_df.tasks = column_list
            column_list = []

            for tuple_of_ratios in self.time_df.ratios:
                string = ' '.join(map(str, tuple_of_ratios))
                column_list.append(string)

            self.time_df.ratios = column_list
                
        else:
            raise ValueError
            
    def get_task_time_series(self, code):
        '''
        Search rows in self.time_df by code.
        Return pandas.Series of weighted task 
        time values with this code.
        Series have datetime index.
        '''
        mask = self.time_df.tasks.apply(lambda x: code in x)
        task_df = self.time_df[mask]
        idx_series = task_df.tasks.apply(lambda x: x.index(code))
        time_list = []
        for idx, ratios, time in zip(idx_series, 
                                     task_df.ratios, 
                                     task_df.total):
            time_list.append(ratios[idx]*time)
        task_df.insert(loc=0, column='time', value=time_list)
        return task_df.time

    @staticmethod
    def get_subcodes(code, codes, with_self=True):
        '''
        Return list of subcodes of selected code from codes.
        Need re.
        '''
        if with_self:
            return [i for i in codes if re.match(code, i)]
        return [i for i in codes if re.match(code+'_', i)]

    def get_end_codes(self, codes):
        '''Return bool list of end values of codes tree'''
        return [len(self.get_subcodes(i, self.summary_df.code,
                                      with_self=False))==0
                for i in self.summary_df.code]
    
    @staticmethod
    def get_rang(time_series, weight=1):
        '''Get priority of elements of time_series with
        respect to values.
        time_series is Pandas.Series
        weight is number or Pandas.Series with same length
        '''
        time_series.loc[time_series == 0] = 0.001
        ans = (10 - np.log(time_series))*1.5*weight
        ans[ans < 0] = 0
        return ans
    
    def set_summary_df(self):
        '''
        Set summary_df self attribute.
        summary_df is pandas.DataFrame based on self.codes_df.
        Raise error if self.codes_df not found (!).
        '''
        self.summary_df = self.codes_df.copy()

        time_list, days_list = [], []

        for code in self.summary_df.code:
            time_series = self.get_task_time_series(code)
            time_list.append(time_series.sum())
            days_list.append(time_series.count())

        self.summary_df['self_time'] = time_list
        self.summary_df['self_days'] = days_list

        time_list, days_list = [], []

        for code in self.summary_df.code:
            subcodes = self.get_subcodes(code, self.summary_df.code)
            mask = self.summary_df.code.apply(lambda code:
                                              code in subcodes)
            total_time = self.summary_df[mask].self_time.sum()
            total_days = self.summary_df[mask].self_days.sum()
            time_list.append(total_time)
            days_list.append(total_days)

        self.summary_df['total_time'] = time_list
        self.summary_df['total_days'] = days_list

        self.summary_df['per_day'] = self.summary_df.total_time / \
            self.summary_df.total_days
        self.summary_df['rang'] = self.get_rang(
            self.summary_df.total_time, self.summary_df.priority)
        
    def get_code_by_name(self, name):
        '''Search code of task by name. Return code or None.
        name is str'''
        ans = self.summary_df[self.summary_df.task == name].code
        if ans.count():
            return ans.values[0]
        return None

    def get_name_by_code(self, code):
        '''Search name of task by code. Return name or None.
        code is str'''
        ans = self.summary_df[self.summary_df.code == code].task
        if ans.count():
            return ans.values[0]
        return None
    
    def check_task(self, task):
        '''Return code of task or raise ValueError.
        Search code in self.summary_df.
        Task is string. May be:
        1. string representation of self.summary_df index
        ('0', '1', '2'...);
        2. value from self.summary_df.task
        ('python', 'machine_learning'...);
        3. directly code from self.summary_df.code
        ('0_0_0_2', '0_1'...)
        '''
        if task.isnumeric():
            task = int(task)
            code = self.summary_df.code.loc[task]
        elif task in self.summary_df.task.values:
            code = self.get_code_by_name(task)
        elif task in self.summary_df.code.values:
            code = task
        else:
            raise ValueError
        return code
    
    def drop_last_row(self, df='time_df'):
        '''drop last row from selected dataframe'''
        if df == 'time_df':
            self.time_df = self.time_df[:-1]
        elif df == 'codes_df':
            self.codes_df = self.codes_df[:-1]
        else:
            raise ValueError
        
    def upd_time_df(self, task, time):
        '''
        Load data without time_df preprocessing,
        add or replace last row of self.time_df and
        save data without time_df preprocessing.
        
        Need datetime as dt (using today date).
        
        path, task (see self.check_task) and time are strings.
        time is string representation of float.
        '''
        #input check block
        code = self.check_task(task)
        time = float(time)

        date = dt.datetime.today().strftime('%Y-%m-%d')
        self.load_data(preprocessing=False)
        last_row = self.time_df.iloc[-1]
        if date == last_row.date:
            action = 'updated'
            last_row_ratios = map(float, last_row.ratios.split())
            last_row_tasks = last_row.tasks.split()
            weighted_time = [last_row.total * ratio for 
                             ratio in last_row_ratios]
            if code in last_row_tasks:
                idx = last_row_tasks.index(code)
                weighted_time[idx] += time
                tasks = ' '.join(last_row_tasks)
            else:
                weighted_time.append(time)
                tasks = last_row.tasks + ' ' + code
            total = sum(weighted_time)
            ratios = ' '.join([str(round(time/total, 2)) for
                               time in weighted_time])
            self.drop_last_row(df='time_df')
        else:
            action = 'added'
            total = time
            ratios = '1.0'
            tasks = code
        self.time_df.loc[self.time_df.shape[0]] = (date,
                                                   tasks,
                                                   ratios,
                                                   total)
        self.save_data(preprocessing=False)
        return (date, tasks, ratios, total, action)
            
    def upd_codes_df(self, task, code, priority):
        '''
        Load data without time_df preprocessing,
        add row to self.codes_df and
        save data without time_df preprocessing.
        
        path, task, code, priority are strings.
        priority is string representation of float.
        
        Be careful with input. Checking only priority.
        '''
        #input check block
        priority = float(priority)

        self.load_data(preprocessing=False)
        self.codes_df.loc[self.codes_df.shape[0]] = (task,
                                                     code,
                                                     priority)
        self.save_data(preprocessing=False)
            
    def normalize(self, series):
        return series/series.sum()
            
    def make_recommendation(self):
        '''
        Return random string of task name from self.summary_df
        with respect to tasks rangs.
        
        Need numpy as np
        '''
        predict_base = self.summary_df[self.get_end_codes(
            self.summary_df.code)].loc[:,['task', 'rang']]
        predict_base.rang = self.normalize(predict_base.rang)
        return np.random.choice(predict_base.task, size=1,
                         replace=False, p=predict_base.rang)[0]

