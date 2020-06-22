import datetime as dt


class TimeCounter():
    '''
    Class for counting time.
    Need datetime as dt.
    '''
    pauseFlag = False
    workFlag = False
    pauseTime = 0
    startTime = 0
    roundPlaces = 2

    def work_switch(self):
        '''
        Main time counting method.
        Use to start or stop counting process.
        Return typle of status (str) and time (float).
        If counting not started, time is None.

        Changes class attributes: workFlag, pauseFlag,
        startTime, pauseTime.
        '''
        work_time = None
        if self.workFlag:
            if self.pauseFlag:
                self.pause()
            self.workFlag = False
            status = 'stopped'
            work_time = self.get_work_time()
        else:
            self.workFlag = True
            self.startTime = dt.datetime.now().timestamp()
            self.pauseTime = 0
            status = 'started'
        return (status, work_time)
            
    def pause(self):
        '''
        Time counting method.
        Use to pause or resume counting process.
        Return typle of status (str) and time (float).
        If counting not started, time is None

        Changes class attributes: pauseFlag, pauseTime.
        '''
        work_time = None
        if self.workFlag:
            if self.pauseFlag:
                self.pauseFlag = False
                status = 'OFF'
            else:
                self.pauseFlag = True
                status = 'ON'
                work_time = self.get_work_time()
            self.pauseTime = dt.datetime.now().timestamp() - \
                             self.pauseTime
            return (status, work_time)

    def minutes_to_hours(self, minutes):
        '''Transfer minutes (number) to hours with a given by
        roundPlaces class attribute accuracy'''
        return round(int(minutes)/60, self.roundPlaces)

    def get_current_time(self):
        '''
        Return current time of work with respect to class flags.
        '''
        if not self.pauseFlag and self.workFlag:
            return self.get_work_time()
        else:
            return None

    def get_work_time(self):
        '''Raw method. Return current time of work.
        Despite the class flags'''
        return round((dt.datetime.now().timestamp() - 
                      self.startTime - self.pauseTime)/3600,
                     self.roundPlaces)

    @staticmethod
    def this_week(series_with_dt_index):
        '''Count work time for this week'''
        last_date = series_with_dt_index.index[-1]
        week_day = dt.datetime.isoweekday(last_date)
        time = series_with_dt_index.iloc[-week_day:].sum()
        return time, week_day
