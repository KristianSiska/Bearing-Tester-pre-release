import datetime
import os

# This will format the daytime so it can be used in naming the files
def getcurrent_datetime(incldue_second = False):
    current_datetime = datetime.datetime.now()
    year = current_datetime.year
    month = current_datetime.month
    day = current_datetime.day
    hour = current_datetime.hour
    minute = current_datetime.minute
    second = current_datetime.second
    if incldue_second == False:
        formatted_datetime = f"{year}{month:02d}{day:02d}_{hour:02d}{minute:02d}"
    else:
        formatted_datetime = f"{year}{month:02d}{day:02d}_{hour:02d}{minute:02d}{second:02d}"
    return formatted_datetime

# making a logger class that will be used to log all the events
# almost everything that will happen will be logged
class Logger(object):
    @staticmethod
    def getcurrent_datetime():
        now = datetime.datetime.now()

        return now.strftime("%y%m%d-%H%M%S")    
        

    def __init__(self,HOME_DIR):
        # address for log files
        self.address = f"{HOME_DIR}\\logs\\"
        
        os.makedirs(self.address, exist_ok=True)
        # filename will be based on current year month day hour...
        self.name = self.getcurrent_datetime() + ".txt"

    def write(self, message):
        with open(os.path.join(self.address, self.name), "ab") as log:
            log.write(f"{Logger.getcurrent_datetime()} -- {message}\n".encode())



            