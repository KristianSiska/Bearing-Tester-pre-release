#
#
#
#
#



# IMPORTS # 
import time

import win32api
from assets.modules.data_module import *
from assets.modules.logger import getcurrent_datetime
import os

import sys

import customtkinter

from PyQt5.QtWidgets import QApplication

# PIL for images
from PIL import Image, ImageTk

import traceback


# EXCEL libraries
import pandas as pd
import openpyxl
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import minimalmodbus
import serial.tools.list_ports


import numpy as np


#delta_t = 1.0193
delta_t = 0.25

ALL_BEARING_TORQUE = 0.000125
TOTAL_ROTATIONAL_MOMENT = 0.00000572
AERODYNAMIC_FRICTION_FORCE_RADIUS = 0.0175
WIDTH_OF_FLYWHEEL = 0.029
AERODYNAMIC_FRICTION_DRAG_AREA = 0.003830125
AERODYNAMIC_FRICTION_DRAG_COEFICIENT = 0.00250
AIR_DENSITY = 1.23



def predict_speed(starting_val, steps, interval):
    # Constants
    

    # Convert starting value to angular velocity in rad/s
    starting_angular_velocity = starting_val * 2 * np.pi
    
    # Initialize angular velocity
    angular_velocity = starting_angular_velocity
    
    rps_list = []
    rps = starting_angular_velocity / (2 * np.pi)
    rps_list.append(rps)

    # Loop through steps to predict speed
    for i in range(steps):
        # Calculate tangential speed
        tangential_speed = AERODYNAMIC_FRICTION_FORCE_RADIUS * angular_velocity
        
        # Calculate aerodynamic drag torque
        aero_drag_torque = 0.5 * AIR_DENSITY * AERODYNAMIC_FRICTION_DRAG_COEFICIENT * AERODYNAMIC_FRICTION_DRAG_AREA * tangential_speed**2

        # Calculate total torque
        total_torque = aero_drag_torque + ALL_BEARING_TORQUE

        # Calculate angular acceleration
        angular_acceleration = total_torque / TOTAL_ROTATIONAL_MOMENT

        # Update angular velocity using Euler's method
        angular_velocity -= interval * angular_acceleration
        
        # Convert angular velocity to revolutions per second (RPS)
        rps = angular_velocity / (2 * np.pi)
        rps_list.append(rps)

    return rps_list


def calculate_deceleration(rotations, times, starting_value):
    normal_deceleration = predict_speed(starting_val=starting_value, interval=delta_t, steps=len(times))

    #print(normal_deceleration)

    for i in range(len(times)):
        if rotations[i] >= normal_deceleration[i]:
            
            print(f"good {rotations[i]} :  {normal_deceleration[i]}")
        else:
            print('bad  ',rotations[i], ":  ", normal_deceleration[i])
            return False
    
    return True


def assess_bearing_condition(rotations, times, starting_value):
    
    result = calculate_deceleration(rotations=rotations, times=times, starting_value=starting_value) 

    if result:
        return "Passed"
    else:
        return "Failed"



def find_tester_port():
        # Get a list of all available COM ports
        ports = serial.tools.list_ports.comports()

        # Iterate through each port and check for "TESTER" in the description
        for port in ports:
            if "CH340" in port.description.upper():
                return port.device  # Return the COM port if found
                #return "COM24"
        # Return None if no matching port is found
        return None


#CH340


# Function to perform Modbus write operation
def write_register(register_address, value, instrument):
    instrument.write_register(register_address, value, functioncode=6)
    time.sleep(0.1)  # Wait for device response
# Function to perform Modbus read operation
def read_input_register(register_address, number_of_registers, instrument):
    return instrument.read_registers(register_address, number_of_registers, functioncode=4)

# Perform the specified Modbus operations
def get_data(callback,instrument, delta_t):
    try:
        # Step 1
        write_register(62, 0, instrument=instrument)

        # Step 2
        write_register(64, 1, instrument=instrument)

        # Step 3
        write_register(66, 0, instrument=instrument)

        # Initialize the start time
        start_time = time.time()

        # Step 4
        while True:
            elapsed_time = time.time() - start_time

            wind_speed = read_input_register(5, 1, instrument=instrument)[0]
            #wind_direction = read_input_register(6, 1, instrument=instrument)[0]

            # Calculate the elapsed time
            

            # Execute the callback function with the new data
            callback(wind_speed)

            # Adjust the sleep time to maintain a 0.01-second interval
            sleep_time = max(0, delta_t - elapsed_time)

            # Introduce a delay to achieve the desired interval
            time.sleep(sleep_time)

            # Update the start time for the next iteration
            start_time = time.time()

    except minimalmodbus.ModbusException as e:
        print(f"Modbus communication error: {e}")
        get_data(callback=callback)

    finally:
        instrument.serial.close()


def OperateModbus_thread(self):
    global delta_t
    while True:
        try:
                       
            com_port = find_tester_port()
            baud_rate = 19200
            slave_address = 1  # Device ID


            # Create a Modbus instrument
            instrument = minimalmodbus.Instrument(com_port, slave_address)
            instrument.serial.baudrate = baud_rate
            instrument.serial.timeout = 1  # Set timeout in seconds


            status = "Connected"

    


            
            #longest_str = 22

            self.PortInfoLabel.configure(text = f"Port         : {com_port}(auto)")
            self.StatusInfoLabel.configure(text=f"Status       : {status}")
            get_data(callback=self.filter_data, instrument=instrument, delta_t=delta_t)


        except:
            self.PortInfoLabel.configure(text = f"Port         : None")
            self.StatusInfoLabel.configure(text=f"Status       : Not Connected")
            #print(traceback.format_exc())
            

    

        
        

         
        

script_directory = os.path.dirname(os.path.abspath(__file__))
#Variables:
ProgramName = "Bearing Tester"

FONT = "Consolas"

# setting Constant Width and Height
# from this nummbers will calculated be everything about sizes
SCREEN_WIDTH_DEFAULT  = 1920
SCREEN_HEIGHT_DEFAULT = 1080 


# This is for getting the usable screen size
app = QApplication(sys.argv)
dw = app.desktop()  # dw = QDesktopWidget() also works if app is created

barsize = 23
screen_width = dw.availableGeometry().width()
screen_height =  dw.availableGeometry().height() - barsize #

# getting the usable screen size

app.quit()




corner_val = 10
# It is used in console for debugging
COLOR_RED   = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_BLUE  = "\033[94m"
COLOR_RESET = "\033[0m"

# Define HEX color codes for GUI
color_gray_border = "#3b3b3b"
color_gray_frame  = ""
color_gray_option_menu  = "#48494a"
color_gray_button  = "#121212"
color_gray_button_pressed = "#"

myserial = None

def x(x1):
    return x1/SCREEN_WIDTH_DEFAULT*screen_width

def y(y1):
    return y1/SCREEN_HEIGHT_DEFAULT*screen_height



class App(customtkinter.CTk):#
    def __init__(self):
        global myserial
        
        super().__init__()

        #self.myserial = CustomSerial()
      

        #self.thread_1 = threading.Thread(target=self.myserial.__init__, daemon=True)
#
        ## Start the data acquisition thread
        #self.thread_1.start()


        #threading.Thread
        self.value_hz = "-"
        self.port = "none"
        self.value_rps = "-"

        self.baud_rate = 19200
        self.slave_address = 1  # Device ID

        self.test_status = False


        # window config
        #self.attributes('-fullscreen', True)

        self.title(ProgramName)
        #try:
        #    #self.iconpath = ImageTk.PhotoImage(file=os.path.join(f"{script_directory}\\assets","barani.png"))
        #    #self.wm_iconbitmap()
        #    #self.iconphoto(False, self.iconpath)
        #except:
        #    pass

    #self.iconbitmap()
        self.geometry(f"{screen_width}x{screen_height}")
        

    
        

        

        
        
        
        self.backframe = customtkinter.CTkFrame(self,width=screen_width,height=screen_height,fg_color="black")
        self.backframe.place(x=0,y=0)




        self.configurationFrame = customtkinter.CTkFrame(
            self.backframe,
            width=x(400),
            height=y(1080),
            corner_radius=corner_val,
            bg_color='transparent',
            border_width=2,
            #fg_color  = color_gray_border,
            border_color=(color_gray_border),
            
            )
        self.configurationFrame.place(x = x(0), y=y(0))





        self.configurationTitle = customtkinter.CTkLabel(
            self.configurationFrame,
            width  = x(200),
            height = y(50 ),
            text   = "Configuration",
            font   = (FONT,y(35)),
            anchor = customtkinter.CENTER,

                                                         )

        self.configurationTitle.place(
            x=x(x(400)-x(200)),
            y=y(40),
            anchor = customtkinter.CENTER
            )


        self.ConnectionStatusFrame = customtkinter.CTkFrame(
            self.backframe,
            width=x(450),
            height=y(220),
            corner_radius=corner_val,
            bg_color='transparent',
            border_width=2,
            #fg_color  = color_gray_border,
            border_color=(color_gray_border),
            
            )


        self.ConnectionStatusFrame.place(x = x(410), y=y(0))

        self.ConnectionLabel = customtkinter.CTkLabel(
            master = self.ConnectionStatusFrame,
            width = x(430),
            height = y(50),
            text = "Connection",
            font = (FONT, 40)
                )
        self.ConnectionLabel.place(x=x(10), y=y(10))



        self.ConnectionInfoFrame = customtkinter.CTkFrame(
            self.ConnectionStatusFrame,
            width=x(430),
            height=y(130),
            corner_radius=corner_val,
            bg_color='transparent',
            border_width=2,
            #fg_color  = color_gray_border,
            border_color=(color_gray_border),
            
            )
        self.ConnectionInfoFrame.place(x=x(10), y=y(80))
        
        self.CommunicationInfoLabel = customtkinter.CTkLabel(
            master = self.ConnectionInfoFrame,
            width = x(400),
            height = y(30),
            text = f"Comunication : Serial" ,
            font = (FONT, 25),
            anchor = "w",
            compound ="left",

        )
        self.CommunicationInfoLabel.place(x=x(12), y=y(10))

        self.StatusInfoLabel = customtkinter.CTkLabel(
            master = self.ConnectionInfoFrame,
            width = x(400),
            height = y(30),
            text = f"Status       : Not Connected" ,
            font = (FONT, 25),
            anchor = "w",
            compound ="left",

        )
        self.StatusInfoLabel.place(x=x(12), y=y(40))

        self.PortInfoLabel = customtkinter.CTkLabel(
            master = self.ConnectionInfoFrame,
            width = x(400),
            height = y(30),
            text = f"Port         : None" ,
            font = (FONT, 25),
            anchor = "w",
            compound ="left",

        )
        self.PortInfoLabel.place(x=x(12), y=y(70))




        self.ResultFrame = customtkinter.CTkFrame(
            self.backframe,
            width=x(550),
            height=y(220),
            corner_radius=corner_val,
            bg_color='transparent',
            border_width=2,
            #fg_color  = color_gray_border,
            border_color=(color_gray_border),
            
            )
        self.ResultFrame.place(x = x(870), y=y(0))


        self.ResultLabel = customtkinter.CTkLabel(
            master = self.ResultFrame,
            width = x(530),
            height = y(50),
            text = "Results",
            font = (FONT, 40)
                )
        self.ResultLabel.place(x=x(10), y=y(10))

        self.ResultInfoFrame = customtkinter.CTkFrame(
            self.ResultFrame,
            width=x(530),
            height=y(130),
            corner_radius=corner_val,
            bg_color='transparent',
            border_width=2,
            #fg_color  = color_gray_border,
            border_color=(color_gray_border),
            
            )
        self.ResultInfoFrame.place(x=x(10), y=y(80))

        self.ResultInfoText = customtkinter.CTkLabel(
            master = self.ResultInfoFrame,
            width= x(500),
            height=y(110),
            font = (FONT, 50),
            text="Waiting For Start",

        )
        self.ResultInfoText.place(x=x(10), y=y(10))

        self.ActualValueFrame = customtkinter.CTkFrame(
            self.backframe,
            width=x(480),
            height=y(220),
            corner_radius=corner_val,
            bg_color='transparent',
            border_width=2,
            #fg_color  = color_gray_border,
            border_color=(color_gray_border),
            
            )
        self.ActualValueFrame.place(x = x(1430), y=y(0))

        self.ActualValueLabel = customtkinter.CTkLabel(
            master = self.ActualValueFrame,
            width = x(460),
            height = y(50),
            text = "Values",
            font = (FONT, 40)
        )
        self.ActualValueLabel.place(x=x(10), y=y(10))



        self.ValuesInfoFrame = customtkinter.CTkFrame(
            self.ActualValueFrame,
            width=x(460),
            height=y(130),
            corner_radius=corner_val,
            bg_color='transparent',
            border_width=2,
            #fg_color  = color_gray_border,
            border_color=(color_gray_border),
            
            )
        self.ValuesInfoFrame.place(x=x(10), y=y(80))

        self.ValuesInfoLabel = customtkinter.CTkLabel(
            master = self.ValuesInfoFrame,
            width = x(400),
            height = y(100),
            text = f"{self.value_hz}{' '*(5-len(str(self.value_hz)))} hz" ,
            font = (FONT, 50),
            anchor = "center",
            compound ="center",

        )
        self.ValuesInfoLabel.place(x=x(12), y=y(10))





# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#                      GRAPH FRAME                        #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
        self.GraphFrame = customtkinter.CTkFrame(
            self.backframe,
            width         = x(1500),
            height        = y(850),
            corner_radius = corner_val,
            bg_color      = "transparent",
            border_width  = 2,
            border_color  = color_gray_border,
            
        )
        self.GraphFrame.place(x=x(410),y=y(230))



   

        self.x_data = []
        self.y_data = []
        self.y_data_correct_picker = []
        self.correct_y_data = []
        x_size = int(x(1480))
        y_size = int(y(820))

        # Create figure and axis
        self.fig, self.ax = plt.subplots(figsize=(x_size / 100, y_size /100))
        self.fig.patch.set_facecolor('#1E1E1E')
        self.ax.set_facecolor('#1E1E1E')

        # Plot the initial lines
        line_width = 1
        self.plot, = self.ax.plot([], [], label='Rotation in hz', color='red', marker="o", linestyle="-", )
        self.normal_plot, = self.ax.plot([], [], label='Normal line', color='white', marker="x", linestyle="-", linewidth=4)
        self.ax.legend()
        if not hasattr(self, 'legend_added'):
            
            self.ax.set_xlabel('Time[s]', color='white')
            self.ax.set_ylabel('Speed[Hz]', color='white')
            self.ax.set_title('Change in time[Hz/s]', color='white')

            # Make numbers white
            for label in (self.ax.get_xticklabels() + self.ax.get_yticklabels()):
                label.set_color('white')

            # Add grid
            self.ax.grid(True, linestyle='--', alpha=0.7)
            try:
                self.ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
            except:
                ...
            
            # Update the legend with the modified label for the first line
            self.ax.legend()

            # Set the flag to prevent adding legend again
            self.legend_added = True


       
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.GraphFrame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.configure(width=x_size, height=y_size)
        self.canvas_widget.place(x=x(10), y=y(10))

        self.data_thread = threading.Thread(target=OperateModbus_thread, args=(self,), daemon=True)

        # Start the data acquisition thread
        self.data_thread.start()

        
        

        self.canvas.draw_idle()
        self.canvas.draw()
        self.fig.tight_layout()



    def update_plot(self, wind_speed):
       
        
       
     
            
        # Update the plot with the new data
        self.x_data.append(len(self.x_data)/(1/delta_t) + 1)
        
        self.y_data.append(wind_speed)

        try:
            self.correct_y_data = predict_speed(self.y_data[0], len(self.x_data)-1, delta_t)
            #self.y_data_correct_picker.append(self.correct_y_data[len(self.x_data)])
            
            
            self.normal_plot.set_data(self.x_data, self.correct_y_data)
        except:
            print(traceback.format_exc())
        # Update the plot
        
        self.plot.set_data(self.x_data, self.y_data)
        
        
        
        
        self.ax.relim()
        self.ax.autoscale_view(True, True, True)
        self.canvas.draw()

        
        
        
    



    


    def end_measurement(self, data):
        
        
        
        
        data = f"{getcurrent_datetime(incldue_second=True)}\n{data}\nend\n"
        dialog = customtkinter.CTkInputDialog(text="Name:", title="Name")
        safe_save_to_csv(f"{dialog.get_input()}.csv", data=data, data_mode="a")
        

    def filter_data(self, wind_speed):
        
        self.value_hz = wind_speed/100



        self.min_start_value = 45
        self.test_start_value = 100
        self.test_end_value = 4
       

        
        
        if self.value_hz < self.test_end_value:
            if self.test_status:
                
                try:
                    x_data_int = []
                    x_data_int = self.x_data
                    y_data_int = self.y_data
                    last_x = int(self.x_data[-1])
                    
                    #if last_x >= self.good_min_value:
                    #    self.ResultInfoText.configure(text="Passed", text_color = "green")
                    #else:
                    #    self.ResultInfoText.configure(text="Failed", text_color = "red")
                    result =assess_bearing_condition(
                       rotations=self.y_data, times=self.x_data, starting_value=self.y_data[0]
                    )
                    color = "blue"
                    if "Fail" in result:
                        color = "red"
                    elif "Pass" in result:
                        color = "green"
                    self.ResultInfoText.configure(text=result, text_color = color
                    )
                    data_str = ""
                    for i in range(len(self.x_data)):
                        data_str += f"{self.x_data[i]};{self.y_data[i]};\n"

                    self.end_measurement(data=data_str)
                except ValueError:
                    ...

                #self.y_data = []
                #self.x_data = []

            self.test_status = False
            self.data_stream = False
            self.last_val = 0
            
            #test_data = []






        if self.value_hz >= self.min_start_value:
            self.data_stream = True
        



        if self.data_stream:
            if self.value_hz <= self.test_end_value:
                self.data_stream = False
         
            if self.value_hz < self.last_val:
           
                
                #if self.value_hz < self.test_start_value:
                    
                self.test_status = True
                self.ResultInfoText.configure(text="Testing...", text_color = "white")
            else:
                print(self.value_hz, " : ", self.last_val)
                self.y_data = []
                self.x_data = []
                self.ax.relim()
                self.plot.set_data(self.x_data, self.y_data)
                #self.canvas.draw_idle()
                self.canvas.draw()
                self.ResultInfoText.configure(text="Starting Test", text_color = "white")

        self.last_val = self.value_hz
        

        if self.test_status:
            
            self.update_plot(self.value_hz)


        self.ValuesInfoLabel.configure(text=f"{self.value_hz}{' '*(5-len(str(self.value_hz)))} hz")

    
    

       


if __name__ == "__main__":
    app = App()
    app.mainloop()
