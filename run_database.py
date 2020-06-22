from data_processor import DataProcessor
from time_counter import TimeCounter
from visualizer import Visualizer

import datetime as dt
import logging
import math
import os
import re
import random
import sys

import matplotlib.dates
import matplotlib.pyplot
import numpy as np
import pandas as pd


class DataBase(TimeCounter, DataProcessor, Visualizer):
    '''Class for processing user commands.'''
    commandsDict = {'/work (/w)': 'start or stop session',
                   '/pause (/p)': 'pause or resume session',
                   '/hours (/h)': 'convert minutes to hours',
                   '/setrp (/rp)': 'set round places.\n'+ \
                        '    syntax: /rp {int}',
                   '/check (/c)': 'check current working hours',
                   '/exit': 'break the main function',
                   '/recommend (/r)': 'make recommendation for work',
                   '/drop': 'drop last row from selected DataFrame'+ \
                        '(time_df (by defoult) or codes_df).\n' + \
                        '    syntax: /drop [{df_name}]',
                   '/updt (/add)': 'add or update last row from time_df\n' + \
                        '    syntax: /ass {task} {time};\n' + \
                        '    task may be index of summary_df, name or code.',
                   '/updc': 'add row to codes_df.\n' + \
                        '    syntax: /updc {task} {code} {priority}',
                   '/timedf': 'fast-load and show time_df',
                   '/codesdf': 'fast-load and show codes_df',
                   '/summary (/s)': 'show summary_df',
                    '/week':'show work time for this week',
                    '/lineplot (/lp)': 'Draw lineplot date/hours.\n' + \
                        '    syntax: /lp [{period} [{smooth_flag} ' + \
                        '[*tasks]]].\n    period: full, year, month,' + \
                        'week;\n    smooth: true/false or 1/0;\n' + \
                        '    task may be index of summary_df, name or code.',
                    '/explineplot (/elp)': 'Draw expanded lineplot. ' + \
                        'Syntax like /lineplot',
                    '/scplot (/scp)': 'Draw scatterplot. ' + \
                        'Syntax like /lineplot without {smooth_flag}',
                    '/sumhourshist (/shh)': 'Draw histogramm of summary hours',
                    '/derdayhist (/dph)': 'Draw histogramm of hours per day',
                    '/worksessionhist (/wsh)': 'Draw work session time histogramm'}
    
    def __init__(self, rp=2, path=''):
        self.roundPlaces = rp
        self.path = path
        pd.set_option('mode.chained_assignment', None)
        self.load_data(preprocessing=True)
        self.set_summary_df()
        self.save_data(preprocessing=True)
        logging.basicConfig(format = u'[%(asctime)s] %(message)s',
            filename=self.path+"work.log", level=logging.INFO)
        
    @staticmethod
    def upd_log(msg, make_output=False):
        logging.info(msg)
        if make_output:
            print(msg)
        
    def cmd_help(self):
        self.upd_log('Help requested', make_output=False)
        for key, value in self.commandsDict.items():
            print('{0} - {1}'.format(key, value))
            
    def cmd_work(self):
        status, time = self.work_switch()
        if status == 'started':
            self.upd_log('Time counting ' + status, make_output=True)
        else:
            self.upd_log('Time counting ' + status + ' [{}]'.format(time), 
                         make_output=True)
            
    def cmd_pause(self):
        try:
            status, time = self.pause()
            if status == 'OFF':
                self.upd_log('Pause ' + status, make_output=True)
            else:
                self.upd_log('Pause ' + status + ' [{}]'.format(time), 
                             make_output=True)
        except:
            print('Counting not started')
            
    def cmd_setrp(self, full_input):
        try:            
            value = int(full_input[1])
            if value > 0:
                self.roundPlaces = value
                self.upd_log('Round places set to {}'.format(value))
            else:
                raise ValueError
        except:
            print('Plese, use /rp {value = integer > 0}')
            
    def cmd_check(self):
        time = self.get_current_time()
        self.upd_log('Current time is [{}]'.format(time), make_output=True)
        
    def cmd_hours(self, full_input):
        try:            
            minutes = float(full_input[1])
            if minutes >= 0:
                print('[{}] minutes is [{}] hours'.format(minutes,
                    self.minutes_to_hours(minutes)))
            else:
                raise ValueError
        except:
            print('Plese, use /h {value >= 0}')
            
        
    def cmd_recommend(self):
        rec = self.make_recommendation()
        print('Try some {}!'.format(rec))
        self.upd_log('Recommendation requested ({})'.format(rec),
                     make_output=False)
            
    def cmd_drop(self, df_name='time_df'):
        try:
            self.load_data(preprocessing=False)
            self.drop_last_row(df=df_name)
            self.save_data(preprocessing=False)
            self.upd_log('Last row from {} was dropped!'.format(df_name), 
                         make_output=True)
        except:
            print('Incorrect input.')
            self.close_data()

    def cmd_updt(self, full_input):
        try:
            task = full_input[1]
            time = full_input[2]
            date, tasks, ratios, \
                total, action = self.upd_time_df(task=task, time=time)
            self.upd_log(
                'Row «{} - {} - {} - {}» was {} in time_df!'.format(
                date, tasks, ratios, total, action), make_output=True)
        except IndexError:
            print('Incorrect input. Please, use /updt {task_name} {time}')

    def cmd_updc(self, full_input):
        try:
            task = full_input[1]
            code = full_input[2]
            priority = full_input[3]
            self.upd_codes_df(task=task, code=code, priority=priority)
            self.upd_log(
                'Row «{} - {} - {}» was added to codes_df!'.format(
                task, code, priority), make_output=True)
        except:
            print('Incorrect input.',
                  'Please, use /updc {task_name} {code} {priority}')

    def cmd_timedf(self):
        self.load_data(preprocessing=False)
        print(self.time_df)
        self.close_data()
        self.upd_log('Data was fast-loaded and closed to show time_df')

    def cmd_codesdf(self):
        self.load_data(preprocessing=False)
        print(self.codes_df)
        self.close_data()
        self.upd_log('Data was fast-loaded and closed to show codes_df')

    def cmd_lineplot(self, full_input):
        try:
            self.load_data(preprocessing=True)
            if len(full_input) == 1:
                self.lineplot()
            elif len(full_input) == 2:
                self.lineplot(period=full_input[1])
            elif len(full_input) == 3:
                smooth = full_input[2] in ('true', '1')
                self.lineplot(period=full_input[1],
                              smooth=smooth)
            else:
                smooth = full_input[2] in ('true', '1')
                self.lineplot(*full_input[3:],
                              period=full_input[1],
                              smooth=smooth)
            self.close_data()
            self.upd_log('Lineplot was drawn')
        except ValueError:
            print('Incorrect input!',
                  'Use /lp [{period} [{smooth_flag} [*tasks]]]')

    def cmd_explineplot(self, full_input):
        try:
            self.load_data(preprocessing=True)
            if len(full_input) == 1:
                self.expanding_lineplot()
            elif len(full_input) == 2:
                self.expanding_lineplot(period=full_input[1])
            elif len(full_input) == 3:
                smooth = full_input[2] in ('true', '1')
                self.expanding_lineplot(period=full_input[1],
                                        smooth=smooth)
            else:
                smooth = full_input[2] in ('true', '1')
                self.expanding_lineplot(*full_input[3:],
                                        period=full_input[1],
                                        smooth=smooth)
            self.close_data()
            self.upd_log('Explineplot was drawn')
        except ValueError:
            print('Incorrect input!',
                  'Use /elp [{period} [{smooth_flag} [*tasks]]]')

    def cmd_scplot(self, full_input):
        try:
            self.load_data(preprocessing=True)
            if len(full_input) == 1:
                self.scatterplot()
            elif len(full_input) == 2:
                self.scatterplot(period=full_input[1])
            else:
                self.scatterplot(*full_input[2:],
                                 period=full_input[1])
            self.close_data()
            self.upd_log('Scatterplot was drawn')
        except ValueError:
            print('Incorrect input!',
                  'Use /scp [{period} [*tasks]]')

    def cmd_sumhourshist(self):
        self.hist_of_summary_hours()
        self.upd_log('Sumhourshist was drawn')

    def cmd_perdayhourshist(self):
        self.hist_of_hours_per_day()
        self.upd_log('Perdayhourshist was drawn')

    def cmd_worksessionhist(self, full_input):
        try:
            self.load_data(preprocessing=True)
            if len(full_input) == 1:
                self.work_session_hist()
            elif len(full_input) == 2:
                self.work_session_hist(period=full_input[1])
            else:
                self.work_session_hist(period=full_input[1],
                                       task=full_input[2])
            self.close_data()
            self.upd_log('Worksessionhist was drawn')
        except ValueError:
            print('Incorrect input!',
                  'Use /wsh [{period} [{task}]]')

    def cmd_week(self):
        self.load_data(preprocessing=True)
        series = self.time_df.total
        self.close_data()
        time, days = self.this_week(series)
        print("It's [{}] hours by {} days!".format(time, days))
        self.upd_log('Week request: {} h by {} d'.format(time, days))
        
    def input_processing(self):
        print('DataBase is running. Use /help to see available commands')
        while True:
            full_input = input().lower().split()
            if full_input:
                command = full_input[0]
            else:
                continue
            
            if command == '/help':
                self.cmd_help()
            elif command in ('/work', '/w'):
                self.cmd_work()
            elif command in ('/pause', '/p'):
                self.cmd_pause()
            elif command in ('/setrp', '/rp'):
                self.cmd_setrp(full_input)
            elif command in ('/check', '/c'):
                self.cmd_check()
            elif command in ('/hours', '/h'):
                self.cmd_hours(full_input)
            elif command in ('/recommend', '/r'):
                self.cmd_recommend()
            elif command == '/drop':
                if len(full_input) == 1:
                    self.cmd_drop()
                else:
                    self.cmd_drop(df_name=full_input[1])
            elif command in ('/updt', '/add'):
                self.cmd_updt(full_input)
            elif command == '/updc':
                self.cmd_updc(full_input)
            elif command == '/timedf':
                self.cmd_timedf()
            elif command == '/codesdf':
                self.cmd_codesdf()
            elif command in ('/summary', '/s'):
                print(self.summary_df)
            elif command in ('/lineplot', '/lp'):
                self.cmd_lineplot(full_input)
            elif command in ('/explineplot', '/elp'):
                self.cmd_explineplot(full_input)
            elif command in ('/sumhourshist', '/shh'):
                self.cmd_sumhourshist()
            elif command in ('/perdayhourshist', '/pdh'):
                self.cmd_perdayhourshist()
            elif command in ('/worksessionhist', '/wsh'):
                self.cmd_worksessionhist(full_input)
            elif command == '/week':
                self.cmd_week()
            elif command == '/exit':
                break
            else:
                print('unknown command')

if __name__ == '__main__':
    db = DataBase()
    db.input_processing()
