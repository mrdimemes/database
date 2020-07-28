import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import datetime as dt


class Visualizer():
    def lineplot(self, *tasks, period='full', smooth=True):
        '''
        Lineplot date/hours. Need self.time_df pandas.DataFrame (!).

        *tasks: tuple of str
        tasks to draw plot. If empty will draw plot of total time
        (plot will contain constant of mean value).
        See DataProcessor.check_task for valid values. Incorrect
        input raise ValueError;

        period: str (values: "full", "year", "month", "week")
        time interval of plot. Incorrect input raise ValueError;
        
        smooth: bool - smooth plot
        '''
        if period == 'full':
            date = self.time_df.total.index[0].strftime('%Y-%m-%d')
        elif period == 'year':
            date = (dt.datetime.today() - 
                    dt.timedelta(days=365)).strftime('%Y-%m-%d')
        elif period == 'month':
            date = (dt.datetime.today() - 
                    dt.timedelta(days=30)).strftime('%Y-%m-%d')
        elif period == 'week':
            date = (dt.datetime.today() - 
                    dt.timedelta(days=7)).strftime('%Y-%m-%d')
        else:
            raise ValueError
            
        if tasks:
            for task in tasks:
                code = self.check_task(task)
                series = self.get_task_time_series(code)
                series = series.asfreq('1d', fill_value=0)[date:]
                if smooth:
                    series = series.rolling(7, min_periods=1).mean()
                name = self.get_name_by_code(code)
                plt.plot(series, label=name)
            plt.legend()
        else:
            series = self.time_df.total[date:]
            if smooth:
                series = series.rolling(7, min_periods=1).mean()
            plt.plot(series)
            mean = series.mean()
            series = series.apply(lambda x: mean)
            plt.plot(series, '--r', linewidth=1)
        plt.grid(True)
        plt.xlabel('date', fontsize=15)
        plt.ylabel('hours', fontsize=15)
        plt.title('Lineplot', fontsize=17)
        plt.gcf().autofmt_xdate()
        plt.show()
        
    def expanding_lineplot(self, *tasks, period='full', smooth=True):
        '''
        Expandind lineplot date/sum_of_hours.
        Need self.time_df pandas.DataFrame (!).

        *tasks: tuple of str
        tasks to draw plot. If empty will draw plot of total time
        (plot will contain line of mean value).
        See DataProcessor.check_task for valid values. Incorrect
        input raise ValueError;

        period: str (values: "full", "year", "month", "week")
        time interval of plot. Incorrect input raise ValueError;
        
        smooth: bool - smooth plot
        '''
        if period == 'full':
            date = self.time_df.total.index[0].strftime('%Y-%m-%d')
        elif period == 'year':
            date = (dt.datetime.today() - 
                    dt.timedelta(days=365)).strftime('%Y-%m-%d')
        elif period == 'month':
            date = (dt.datetime.today() - 
                    dt.timedelta(days=30)).strftime('%Y-%m-%d')
        elif period == 'week':
            date = (dt.datetime.today() - 
                    dt.timedelta(days=7)).strftime('%Y-%m-%d')
        else:
            raise ValueError
            
        if tasks:
            for task in tasks:
                code = self.check_task(task)
                series = self.get_task_time_series(code)
                series = series.asfreq('1d', fill_value=0)
                series = series.expanding().sum()[date:]
                if smooth:
                    series = series.rolling(7, min_periods=1).mean()
                name = self.get_name_by_code(code)
                plt.plot(series, label=name)
            plt.legend()
        else:
            series = self.time_df.total
            series = series.expanding().sum()[date:]
            if smooth:
                series = series.rolling(7, min_periods=1).mean()
            plt.plot(series)
            plt.plot(series.iloc[[0,-1]], '--r', linewidth=1)
        plt.grid(True)
        plt.xlabel('date', fontsize=15)
        plt.ylabel('hours', fontsize=15)
        plt.title('Expanding lineplot', fontsize=17)
        plt.gcf().autofmt_xdate()
        plt.show()
        
    def scatterplot(self, *tasks, period='full'):
        '''
        Expandind lineplot date/sum_of_hours.
        Need self.time_df pandas.DataFrame (!).

        *tasks: tuple of str
        tasks to draw plot. If empty will draw plot of total time
        (plot will contain constant of mean value).
        See DataProcessor.check_task for valid values. Incorrect
        input raise ValueError;

        period: str (values: "full", "year", "month", "week")
        time interval of plot. Incorrect input raise ValueError;
        '''
        if period == 'full':
            date = self.time_df.total.index[0].strftime('%Y-%m-%d')
        elif period == 'year':
            date = (dt.datetime.today() - 
                    dt.timedelta(days=365)).strftime('%Y-%m-%d')
        elif period == 'month':
            date = (dt.datetime.today() - 
                    dt.timedelta(days=30)).strftime('%Y-%m-%d')
        elif period == 'week':
            date = (dt.datetime.today() - 
                    dt.timedelta(days=7)).strftime('%Y-%m-%d')
        else:
            raise ValueError
            
        if tasks:
            for task in tasks:
                code = self.check_task(task)
                series = self.get_task_time_series(code)
                series = series.asfreq('1d', fill_value=0)[date:]
                name = self.get_name_by_code(code)
                plt.plot(series, 'o', label=name)
            plt.legend()
        else:
            series = self.time_df.total[date:]
            plt.plot(series, 'o')
            mean = series.mean()
            series = series.apply(lambda x: mean)
            plt.plot(series, '--r', linewidth=1)
        plt.grid(True)
        plt.xlabel('date', fontsize=15)
        plt.ylabel('hours', fontsize=15)
        plt.title('Scatterplot', fontsize=17)
        plt.gcf().autofmt_xdate()
        plt.show()
        
    def hist_of_summary_hours(self):
        '''
        Histogramm of end tasks tree summary hours.
        Need self.summary_df pandas.DataFrame (!).
        '''
        mask = self.get_end_codes()
        plt.bar(self.summary_df.task[mask],
                self.summary_df[mask].total_time)
        plt.gcf().autofmt_xdate()
        plt.xlabel('task', fontsize=15)
        plt.ylabel('hours', fontsize=15)
        plt.title('Histogram of summary time', fontsize=17)
        plt.show()
        
    def hist_of_hours_per_day(self):
        '''
        Histogramm of end tasks tree hours per day.
        Need self.summary_df pandas.DataFrame (!).
        '''
        mask = self.get_end_codes()
        plt.bar(self.summary_df.task[mask],
                self.summary_df[mask].per_day)
        plt.gcf().autofmt_xdate()
        plt.xlabel('task', fontsize=15)
        plt.ylabel('hours', fontsize=15)
        plt.title('Histogram of time per day', fontsize=17)
        plt.show()
        
    def work_session_hist(self, task='all', period='full'):
        '''
        Histogramm of work session time.
        Need self.time_df pandas.DataFrame (!).

        task: str (values: "all" or DataProcessor.check_task values)
        task to draw hist. Incorrect input raise ValueError;

        period: str (values: "full", "year", "month", "week")
        time interval of hist base. Incorrect input raise ValueError;
        '''
        if period == 'full':
            date = self.time_df.total.index[0].strftime('%Y-%m-%d')
        elif period == 'year':
            date = (dt.datetime.today() - 
                    dt.timedelta(days=365)).strftime('%Y-%m-%d')
        elif period == 'month':
            date = (dt.datetime.today() - 
                    dt.timedelta(days=30)).strftime('%Y-%m-%d')
        elif period == 'week':
            date = (dt.datetime.today() - 
                    dt.timedelta(days=7)).strftime('%Y-%m-%d')
        else:
            raise ValueError
        
        if task == 'all':
            series = self.time_df.total[date:]
            label = 'all'
        else:
            code = self.check_task(task)
            series = self.get_task_time_series(code)[date:]
            label = self.get_name_by_code(code)
            
        plt.hist(series, 12, label=label)
        plt.xlabel('hours', fontsize=15)
        plt.title('Work session time histogram\n({})'.format(period),
                  fontsize=17)
        plt.legend()
        plt.show()


