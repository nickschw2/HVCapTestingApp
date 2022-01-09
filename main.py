import tkinter as tk
from tkinter import ttk, filedialog

# Import statements for creating plots in tkinter applications
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import time
import os
import nidaqmx
import webbrowser
from constants import *

# Tkinter has quite a high learning curve. If attempting to edit this source code without experience, I highly
# recommend going through some tutorials. The documentation on tkinter is also quite poor, but
# this website has the best I can find (http://www.tcl.tk/man/tcl8.5/TkCmd/contents.htm). At times you may
# need to manually go into the tkinter source code to investigate the behavior/capabilities of some code.

class MainApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('HV Capacitor Testing')

        #Change deault color palette
        self.tk_setPalette(background=grey, foreground=white, activeBackground=lightGrey, activeForeground=white)

        # This line of code is customary to quit the application when it is closed
        self.protocol('WM_DELETE_WINDOW', self.on_closing)

        # Row for user inputs on the top
        self.userInputs = tk.Frame(self, **border_opts)
        self.userInputs.grid(row=0, columnspan=3, sticky='ns', pady=(0, yPaddingFrame))

        # User input fields along with a button for setting them
        self.serialNumberLabel = tk.Label(self.userInputs, text='Cap Serial #:', **text_opts)
        self.chargeVoltageLabel = tk.Label(self.userInputs, text='Charge (kV):', **text_opts)
        self.holdChargeTimeLabel = tk.Label(self.userInputs, text='Hold Charge (s):', **text_opts)

        self.serialNumberEntry = tk.Entry(self.userInputs, width=userInputWidth, **entry_opts)
        self.chargeVoltageEntry = tk.Entry(self.userInputs, width=userInputWidth, **entry_opts)
        self.holdChargeTimeEntry = tk.Entry(self.userInputs, width=userInputWidth, **entry_opts)

        self.userInputOkayButton = tk.Button(self.userInputs, text='Set', command=self.setUserInputs, **button_opts)

        self.serialNumberLabel.pack(side='left')
        self.serialNumberEntry.pack(side='left', padx=(0, userInputPadding))
        self.chargeVoltageLabel.pack(side='left')
        self.chargeVoltageEntry.pack(side='left', padx=(0, userInputPadding))
        self.holdChargeTimeLabel.pack(side='left')
        self.holdChargeTimeEntry.pack(side='left', padx=(0, userInputPadding))
        self.userInputOkayButton.pack(side='left')

        # Column for labels on the left
        self.grid_columnconfigure(0, w=1)
        self.labels = tk.Frame(self, **border_opts)
        self.labels.grid(row=1, column=0)

        # Voltage and current are read from both the power supply and the load
        self.voltageLoadText = tk.StringVar()
        self.voltagePSText = tk.StringVar()
        self.currentLoadText = tk.StringVar()
        self.currentPSText = tk.StringVar()
        self.chargeStateText = tk.StringVar()
        self.countdownText = tk.StringVar()

        self.voltageLoadLabel = tk.Label(self.labels, textvariable=self.voltageLoadText, **text_opts)
        self.voltagePSLabel = tk.Label(self.labels, textvariable=self.voltagePSText, **text_opts)
        self.currentLoadLabel = tk.Label(self.labels, textvariable=self.currentLoadText, **text_opts)
        self.currentPSLabel = tk.Label(self.labels, textvariable=self.currentPSText, **text_opts)
        self.chargeStateLabel = tk.Label(self.labels, textvariable=self.chargeStateText, **text_opts)
        self.countdownLabel = tk.Label(self.labels, textvariable=self.countdownText, **text_opts)

        self.voltageLoadLabel.pack(pady=labelPadding, padx=labelPadding)
        self.voltagePSLabel.pack(pady=labelPadding, padx=labelPadding)
        self.currentLoadLabel.pack(pady=labelPadding, padx=labelPadding)
        self.currentPSLabel.pack(pady=labelPadding, padx=labelPadding)
        self.chargeStateLabel.pack(pady=labelPadding, padx=labelPadding)
        self.countdownLabel.pack(pady=labelPadding, padx=labelPadding)

        # Row for buttons on the bottom
        self.grid_rowconfigure(2, w=1)
        self.buttons = tk.Frame(self)
        self.buttons.grid(row=2, columnspan=3, sticky='ns', pady=(yPaddingFrame, 0))

        # Button definitions and placement
        self.saveLocationButton = tk.Button(self.buttons, text='Save Location',
                                    command=self.setSaveLocation, bg=green, **button_opts)
        self.setPinsButton = tk.Button(self.buttons, text='Set Pins',
                                    command=self.setPins, bg=green, **button_opts)
        self.checklistButton = tk.Button(self.buttons, text='Begin Checklist',
                                    command=self.checklist, bg=green, **button_opts)
        self.chargeButton = tk.Button(self.buttons, text='Charge',
                                    command=self.charge, bg=yellow, **button_opts)
        self.dischargeButton = tk.Button(self.buttons, text='Discharge',
                                    command=self.discharge, bg=orange, **button_opts)
        self.emergency_offButton = tk.Button(self.buttons, text='Emergency Off',
                                    command=self.emergency_off, bg=red, **button_opts)
        self.resetButton = tk.Button(self.buttons, text='Reset',
                                    command=self.reset, bg=red, **button_opts)

        self.saveLocationButton.pack(side='left', padx=buttonPadding)
        self.setPinsButton.pack(side='left', padx=buttonPadding)
        self.checklistButton.pack(side='left', padx=buttonPadding)
        self.chargeButton.pack(side='left', padx=buttonPadding)
        self.dischargeButton.pack(side='left', padx=buttonPadding)
        self.emergency_offButton.pack(side='left', padx=buttonPadding)
        self.resetButton.pack(side='left', padx=buttonPadding)

        self.saveFolderSet = False

        # Menubar at the top
        self.menubar = tk.Menu(self)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label='Open', command=self.readResults)
        self.filemenu.add_command(label='Save', command=self.setSaveLocation)
        self.filemenu.add_separator()
        self.filemenu.add_command(label='Quit', command=self.on_closing)
        self.menubar.add_cascade(label='File', menu=self.filemenu)

        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label='Help', command=self.help)
        self.helpmenu.add_command(label='About...', command=self.openSite)
        self.menubar.add_cascade(label='Help', menu=self.helpmenu)

        self.config(menu=self.menubar)

        # Configure Graphs
        self.grid_rowconfigure(1, w=1)
        self.grid_columnconfigure(1, w=1)
        self.grid_columnconfigure(2, w=1)

        # Plot of charge and discharge
        self.chargePlot = CanvasPlot(self)
        self.dischargePlot = CanvasPlot(self)

        # Create two y-axes for current and voltage
        self.chargeVoltageAxis = self.chargePlot.ax
        self.chargeCurrentAxis = self.chargePlot.ax.twinx()
        self.dischargeVoltageAxis = self.dischargePlot.ax
        self.dischargeCurrentAxis = self.dischargePlot.ax.twinx()

        self.chargeVoltageAxis.tick_params(axis='y', labelcolor=voltageColor)
        self.chargeCurrentAxis.tick_params(axis='y', labelcolor=currentColor)
        self.dischargeVoltageAxis.tick_params(axis='y', labelcolor=voltageColor)
        self.dischargeCurrentAxis.tick_params(axis='y', labelcolor=currentColor)

        self.chargePlot.ax.set_xlabel('Time (s)')
        self.dischargePlot.ax.set_xlabel('Time (s)')

        self.chargeVoltageAxis.set_ylabel('Voltage (kV)', color=voltageColor)
        self.chargeCurrentAxis.set_ylabel('Current (A)', color=currentColor)
        self.dischargeVoltageAxis.set_ylabel('Voltage (kV)', color=voltageColor)
        self.dischargeCurrentAxis.set_ylabel('Current (A)', color=currentColor)

        self.chargePlot.ax.set_title('Charge Plot')
        self.dischargePlot.ax.set_title('Discharge Plot')

        # Create the legends before any plot is made
        self.chargePlot.ax.legend(handles=chargeHandles, loc='lower left')
        self.dischargePlot.ax.legend(handles=dischargeHandles, loc='lower left')

        self.chargePlot.grid(row=1, column=1, sticky='ew', padx=plotPadding)
        self.dischargePlot.grid(row=1, column=2, sticky='ew', padx=plotPadding)


        try:
            # On startup, disable buttons until login is correct
            self.disableButtons()
            self.loggedIn = False
            self.validateLogin()

            self.safetyLights()

            # Reset all fields on startup, including making a connection to NI DAQ
            self.reset()

        except Exception as e:
            print(e)

    def openSite(self):
        webbrowser.open(githubSite)

    def setSaveLocation(self):
        # Creates folder dialog for user to choose save directory
        self.saveFolder = filedialog.askdirectory(initialdir=os.path.dirname(os.path.realpath(__file__)), title='Select directory for saving results.')
        if self.saveFolder != '':
            self.saveFolderSet = True

        # If the user inputs have already been set, enable the checklist button
        if self.userInputsSet:
            self.checklistButton.configure(state='normal', relief='raised')

        # Try setting the pins automatically
        self.setPins()

    def setPins(self):
        # Create popup window with fields for username and password
        self.setPinWindow = tk.Toplevel(padx=setPinsPadding, pady=setPinsPadding)
        self.setPinWindow.title('Set Pins')
        # Bring pop up to the center and top
        self.eval(f'tk::PlaceWindow {str(self.setPinWindow)} center')
        self.setPinWindow.attributes('-topmost', True)

        # Options available for pins and channels to read/write
        inputPinOptions = ['ai0', 'ai1', 'ai2', 'ai3']
        outputPinOptions = ['line0', 'line1']

        inputChannels = ['Load Voltage', 'Power Supply Voltage', 'Load Current', 'Power Supply Current']
        outputChannels = ['Power Supply Switch', 'Load Switch']

        # Labels on the left, dropdowns on the right
        labelFrame = tk.Frame(self.setPinWindow)
        optionMenuFrame = tk.Frame(self.setPinWindow)
        labelFrame.pack(side='left')
        optionMenuFrame.pack(side='left')

        # Initialize empty dictionary for pins
        inputPins = {}
        outputPins = {}
        for i, channel in enumerate(inputChannels):
            channelVariable = tk.StringVar()
            channelVariable.set(inputPinDefaults[channel])
            label = tk.Label(labelFrame, text=channel, **text_opts)
            drop = tk.OptionMenu(optionMenuFrame, channelVariable, *inputPinOptions)

            label.grid(row=i, sticky='w', padx=(0, setPinsPadding))
            drop.grid(row=i, sticky='w', padx=(setPinsPadding, 0))

        for i, channel in enumerate(outputChannels):
            channelVariable = tk.StringVar()
            channelVariable.set(outputPinDefaults[channel])
            label = tk.Label(labelFrame, text=channel, **text_opts)
            drop = tk.OptionMenu(optionMenuFrame, channelVariable, *inputPinOptions)

            label.grid(row=i + len(inputChannels), sticky='w', padx=(0, setPinsPadding))
            drop.grid(row=i + len(inputChannels), sticky='w', padx=(setPinsPadding, 0))


        # login_text = 'Please enter UMD username.'
        # password_text = 'Please enter password.'
        # button_text = 'Login'
        #
        # self.usernameLabel = tk.Label(self.loginWindow, text=login_text, **text_opts)
        # self.usernameEntry = tk.Entry(self.loginWindow, **entry_opts)
        # self.passwordLabel = tk.Label(self.loginWindow, text=password_text, **text_opts)
        # self.passwordEntry = tk.Entry(self.loginWindow, show='*', **entry_opts)
        # self.loginButton = tk.Button(self.loginWindow, text=button_text, command=lambda event='Okay Press': checkLogin(event), **button_opts)
        #
        # # User can press 'Return' key to login instead of loginButton
        # self.loginWindow.bind('<Return>', checkLogin)
        #
        # self.usernameLabel.pack()
        # self.usernameEntry.pack()
        # self.passwordLabel.pack()
        # self.passwordEntry.pack()
        # self.loginButton.pack()

    def saveResults(self):
        # Create a unique identifier for the filename in the save folder
        # Format: date_serialNumber_runNumber.csv
        date = today.strftime('%Y%m%d')
        run = 1
        filename = f'{today}_{self.serialNumber}_{run}.csv'
        while filename in os.listdir(self.saveFolder):
            run += 1
            filename = f'{today}_{self.serialNumber}_{run}.csv'

        # These results are listed in accordance with the 'columns' variable in constants.py
        # If the user would like to add or remove fields please make those changes both here and to 'columns'
        self.results = [self.serialNumber, self.chargeVoltage, self.holdChargeTime,
            self.chargeTime, self.chargeVoltagePS, self.chargeVoltageLoad, self.chargeCurrentPS,
            self.chargeCurrentLoad, self.dischargeTime, self.dischargeVoltageLoad, self.dischargeCurrentLoad]

        # Creates a data frame which is easier to save to csv formats
        results_df = pd.DataFrame([pd.Series(val) for val in self.results]).T
        results_df.columns = columns
        results_df.to_csv(f'{self.saveFolder}/{filename}', index=False)

    # Read in a csv file and plot those results
    def readResults(self):
        readFile = filedialog.askopenfilename(filetypes=[('Comma separated values', '.csv')])
        if readFile != '':
            results_df = pd.read_csv(readFile)

            # Reset program and allow user to reset
            self.reset()
            self.resetButton.configure(state='normal', relief='raised')

            self.serialNumber = results_df['Serial Number'].dropna().values[0]
            self.chargeVoltage = results_df['Charged Voltage (kV)'].dropna().values[0]
            self.holdChargeTime = results_df['Hold Charge Time (s)'].dropna().values[0]
            self.chargeTime = results_df['Charge Time (s)'].dropna().values
            self.chargeVoltagePS = results_df['Charge Voltage PS (V)'].dropna().values
            self.chargeVoltageLoad = results_df['Charge Voltage Load (V)'].dropna().values
            self.chargeCurrentPS = results_df['Charge Current PS (A)'].dropna().values
            self.chargeCurrentLoad = results_df['Charge Current Load (A)'].dropna().values
            self.dischargeTime = results_df['Discharge Time (s)'].dropna().values
            self.dischargeVoltageLoad = results_df['Discharge Voltage (V)'].dropna().values
            self.dischargeCurrentLoad = results_df['Discharge Current (A)'].dropna().values

            # Place values for all user inputs and plots
            self.serialNumberEntry.insert(0, self.serialNumber)
            self.chargeVoltageEntry.insert(0, self.chargeVoltage)
            self.holdChargeTimeEntry.insert(0, self.holdChargeTime)

            self.replotCharge()
            self.replotDischarge()

    def setUserInputs(self):
        # Try to set the user inputs. If there is a ValueError, display pop up message.
        try:
            # If there is an exception, catch where the exception came from
            self.serialNumber = self.serialNumberEntry.get()
            self.userInputError = 'chargeVoltage'
            self.chargeVoltage = float(self.chargeVoltageEntry.get())
            self.userInputError = 'holdChargeTime'
            self.holdChargeTime = float(self.holdChargeTimeEntry.get())

            # Make sure that the serial number matches the correct format, if not raise error
            self.capModel = self.serialNumber[0:3]
            if format.match(self.serialNumber) is None or self.capModel not in maxVoltage:
                self.userInputError = 'serialNumber'
                raise ValueError

            if self.chargeVoltage > maxVoltage[self.capModel]:
                self.userInputError = 'chargeVoltage'
                raise ValueError

            self.userInputsSet = True

            # Check if the save folder has been selected, and if so allow user to begin checklist
            if self.saveFolderSet:
                self.checklistButton.configure(state='normal', relief='raised')

            # Display pop up window to let user know that values have been set
            setUserInputName = 'User Inputs Set!'
            setUserInputText = 'User inputs have been set. They may be changed at any time for any subsequent run.'
            setUserInputWindow = MessageWindow(self, setUserInputName, setUserInputText)

            setUserInputWindow.wait_window()

        # Pop up window for incorrect user inputs
        except ValueError as err:
            def incorrectUserInput(text):
                incorrectUserInputName = 'Invalid Input'
                incorrectUserInputWindow = MessageWindow(self, incorrectUserInputName, text)

                incorrectUserInputWindow.wait_window()

            # Clear the user input fields
            if self.userInputError == 'chargeVoltage':
                self.chargeVoltageEntry.delete(0, 'end')

                incorrectUserInputText = f'Please reenter a valid number for the charge voltage. The maximum voltage for this capacitor is {maxVoltage[self.capModel]} kV.'
                incorrectUserInput(incorrectUserInputText)

            elif self.userInputError == 'holdChargeTime':
                self.holdChargeTimeEntry.delete(0, 'end')

                incorrectUserInputText = 'Please reenter a valid number for the charge time.'
                incorrectUserInput(incorrectUserInputText)

            elif self.userInputError == 'serialNumber':
                self.serialNumberEntry.delete(0, 'end')

                incorrectUserInputText = 'Please reenter a valid format for serial number.'
                incorrectUserInput(incorrectUserInputText)

    # Disable all buttons in the button frame
    def disableButtons(self):
        for w in self.buttons.winfo_children():
            if isinstance(w, tk.Button):
                w.configure(state='disabled', relief='sunken')

    # Enable normal operation of all buttons in the button frame
    def enableButtons(self):
        for w in self.buttons.winfo_children():
            if isinstance(w, tk.Button):
                w.configure(state='normal', relief='raised')

    # Every time an item on the checklist is ticked complete, check to see if the entire list is complete
    def checklistComplete(self):
        complete = False
        complete = all([cb.get() for keys, cb in self.checklist_Checkbuttons.items()])

        # Only if the user inputs are also set will the buttons be enabled
        if complete and self.userInputsSet and len(self.checklist_Checkbuttons) !=0:
            self.enableButtons()

        self.checklist_win.destroy()

    def checklist(self):
        # Any time the checklist is opened, all buttons are disabled except for the save, help, and checklist
        self.disableButtons()
        self.saveLocationButton.configure(state='normal', relief='raised')
        self.checklistButton.configure(state='normal', relief='raised')

        # Top level window for checklist
        self.checklist_win = tk.Toplevel()
        # Bring pop up to the center and top
        self.eval(f'tk::PlaceWindow {str(self.checklist_win)} center')
        self.checklist_win.attributes('-topmost', True)

        # Create a Checkbutton for each item on the checklist
        for i, step in enumerate(checklist_steps):
            # A BooleanVar is linked to each Checkbutton and its state is updated any time a check is changed
            # The completion of the checklist is checked every time a Checkbutton value is changed
            self.checklist_Checkbuttons[f'c{i + 1}'] = tk.BooleanVar()
            button = tk.Checkbutton(self.checklist_win, variable=self.checklist_Checkbuttons[f'c{i + 1}'], text=f'Step {i + 1}: ' + step, font=('Calibri', 12), selectcolor=black)
            button.grid(row=i, column=0, sticky='w')

        # Add okay button to close the window
        self.OKButton = tk.Button(self.checklist_win, text='Okay', command=self.checklistComplete, **button_opts)
        self.OKButton.grid(row=len(checklist_steps) + 1, column=0)

        # I believe wait_window functions to wait for the window to close before the rest of the app can execute the next function
        self.checklist_win.wait_window()

    def charge(self):
        # Popup window appears to confirm charging
        chargeConfirmName = 'Begin charging'
        chargeConfirmText = 'Are you sure you want to begin charging?'
        chargeConfirmWindow = MessageWindow(self, chargeConfirmName, chargeConfirmText)

        cancelButton = tk.Button(chargeConfirmWindow.bottomFrame, text='Cancel', command=chargeConfirmWindow.destroy, **button_opts)
        cancelButton.pack(side='left')

        chargeConfirmWindow.wait_window()

        # If the user presses the Okay button, charging begins
        if chargeConfirmWindow.OKPress:
            # Begin tracking time
            self.beginChargeTime = time.time()
            self.charging = True

            # Reset the charge plot and begin continuously plotting
            self.resetChargePlot()
            self.updateChargePlot()
            self.chargePress = True

    def discharge(self):
        # Only plot discharge and save results if charging
        if self.charging and self.countdownTime <= 0.0:
            # Read from the load
            oscilloscopePins = [inputPinDefaults['Load Voltage'], inputPinDefaults['Load Current']]
            self.dischargeTime, self.dischargeVoltageLoad, self.dischargeCurrentLoad = self.readOscilloscope(oscilloscopePins)

            # Plot results on the discharge graph and save them
            # The only time results are saved is when there is a discharge that is preceded by charge
            self.replotDischarge()
            self.saveResults()

        elif self.charging:
            # Popup window to confirm discharge
            dischargeConfirmName = 'Discharge'
            dischargeConfirmText = 'Are you sure you want to discharge?'
            dischargeConfirmWindow = MessageWindow(self, dischargeConfirmName, dischargeConfirmText)

            cancelButton = tk.Button(dischargeConfirmWindow.bottomFrame, text='Cancel', command=dischargeConfirmWindow.destroy, **button_opts)
            cancelButton.pack(side='left')

            dischargeConfirmWindow.wait_window()

            if dischargeConfirmWindow.OKPress:
                print('Discharge')

            # Read from the load
            oscilloscopePins = [inputPinDefaults['Load Voltage'], inputPinDefaults['Load Current']]
            self.dischargeTime, self.dischargeVoltageLoad, self.dischargeCurrentLoad = self.readOscilloscope(oscilloscopePins)

            # Plot results on the discharge graph and save them
            # The only time results are saved is when there is a discharge that is preceded by charge
            self.replotDischarge()
            self.saveResults()

        # Disable all buttons except for save and help, if logged in
        self.disableButtons()
        if self.loggedIn:
            self.saveLocationButton.configure(state='normal', relief='raised')
            self.resetButton.configure(state='normal', relief='raised')

        self.discharged = True
        self.charging = False

    # Turn on safety lights inside the control room and outside the lab
    def safetyLights(self):
        print('Turn on safety lights')

    def emergency_off(self):
        print('Emergency Off')

    def validateLogin(self):
        # If someone is not logged in then the buttons remain deactivated
        def checkLogin(event):
            # Obtain login status. To change valid usernames and password please see constants.py
            self.username = self.usernameEntry.get()
            self.password = self.passwordEntry.get()
            self.loggedIn = self.username in acceptableUsernames and self.password in acceptablePasswords

            # Once logged in, enable the save location and help buttons
            if self.loggedIn:
                self.loginWindow.destroy()
                self.saveLocationButton.configure(state='normal', relief='raised')

                # Prompt save location after login
                self.setSaveLocation()

            # If incorrect username or password, create popup notifying the user
            else:
                incorrectLoginName = 'Incorrect Login'
                incorrectLoginText = 'You have entered either a wrong name or password. Please reenter your credentials or contact nickschw@umd.edu for help'
                incorrectLoginWindow = MessageWindow(self, incorrectLoginName, incorrectLoginText)

                incorrectLoginWindow.wait_window()

                # Clear username and password entries
                self.usernameEntry.delete(0, 'end')
                self.passwordEntry.delete(0, 'end')

        # Create popup window with fields for username and password
        self.loginWindow = tk.Toplevel(padx=loginPadding, pady=loginPadding)
        self.loginWindow.title('Login Window')

        login_text = 'Please enter UMD username.'
        password_text = 'Please enter password.'
        button_text = 'Login'

        self.usernameLabel = tk.Label(self.loginWindow, text=login_text, **text_opts)
        self.usernameEntry = tk.Entry(self.loginWindow, **entry_opts)
        self.passwordLabel = tk.Label(self.loginWindow, text=password_text, **text_opts)
        self.passwordEntry = tk.Entry(self.loginWindow, show='*', **entry_opts)
        self.loginButton = tk.Button(self.loginWindow, text=button_text, command=lambda event='Okay Press': checkLogin(event), **button_opts)

        # User can press 'Return' key to login instead of loginButton
        self.loginWindow.bind('<Return>', checkLogin)

        self.usernameLabel.pack()
        self.usernameEntry.pack()
        self.passwordLabel.pack()
        self.passwordEntry.pack()
        self.loginButton.pack()

    # Special function for closing the window and program
    def on_closing(self):
        plt.close('all')
        self.quit()
        self.destroy()

    def readSensor(self, pin):
        try:
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_voltage_chan(f'{sensorName}/{pin}')
                value = task.read()

        except:
            print('Cannot connect to NI DAQ')
            if pin == 'ai0':
                value = np.random.rand() * 1000
            elif pin == 'ai1':
                value = powerSupplyVoltage * ( 1 -  np.exp( -self.timePoint / RCTime ) )
            elif pin == 'ai2':
                value = np.random.rand() / 10
            elif pin == 'ai3':
                period = 10 # seconds
                value = np.abs(np.cos(self.timePoint * 2 * np.pi / period))
            else:
                value = 'N/A'

        return value

    # Read oscilloscope data based on pins
    def readOscilloscope(self, pins):
        time = np.linspace(0, 1)
        voltageLoad = 1 - np.exp(-time)
        currentLoad = np.exp(-time)
        return time, voltageLoad, currentLoad

    # The labels for the load and power supply update in real time
    def updateLabels(self):
        loadSuperscript = '\u02E1\u1D52\u1D43\u1D48'
        PSSuperscript = '\u1D56\u02E2'
        self.voltageLoadText.set(f'V{loadSuperscript}: {self.readSensor(inputPinDefaults["Load Voltage"]) / 1000:.2f} kV')
        self.voltagePSText.set(f'V{PSSuperscript}: {self.readSensor(inputPinDefaults["Power Supply Voltage"]) / 1000:.2f} kV')
        self.currentLoadText.set(f'I{loadSuperscript}: {self.readSensor(inputPinDefaults["Load Current"]):.2f} A')
        self.currentPSText.set(f'I{PSSuperscript}: {self.readSensor(inputPinDefaults["Power Supply Current"]):.2f} A')

        # Logic heirarchy for charge state and countdown text
        if self.discharged:
            self.chargeStateText.set('Discharged!')
            self.countdownText.set(f'Coundown: 0.0 s')
        elif self.charged:
            self.chargeStateText.set('Charged')
            self.countdownText.set(f'Coundown: {self.countdownTime:.2f} s')
        else:
            self.chargeStateText.set('Not Charged')
            self.countdownText.set('Countdown: N/A')

    # Removes all lines from a figure
    def clearFigLines(self, fig):
        axes = fig.axes
        for axis in axes:
            if len(axis.lines) != 0:
                for i in range(len(axis.lines)):
                    axis.lines[0].remove()

    def replotCharge(self):
        # Remove lines every time the figure is plotted
        self.clearFigLines(self.chargePlot.fig)

        # Add plots
        self.chargeVoltageAxis.plot(self.chargeTime, self.chargeVoltageLoad / 1000, color=voltageColor)
        self.chargeVoltageAxis.plot(self.chargeTime, self.chargeVoltagePS / 1000, color=voltageColor, linestyle='--')
        self.chargeCurrentAxis.plot(self.chargeTime, self.chargeCurrentLoad, color=currentColor)
        self.chargeCurrentAxis.plot(self.chargeTime, self.chargeCurrentPS, color=currentColor, linestyle='--')
        self.chargePlot.update()

    def replotDischarge(self):
        # Remove lines every time the figure is plotted
        self.clearFigLines(self.dischargePlot.fig)

        # Add plots
        self.dischargeVoltageAxis.plot(self.dischargeTime, self.dischargeVoltageLoad / 1000, color=voltageColor, label='V$_{load}$')
        self.dischargeCurrentAxis.plot(self.dischargeTime, self.dischargeCurrentLoad, color=currentColor, label='I$_{load}$')
        self.dischargePlot.update()

    # Retrieves and processes the data for the charging plot in a continuous loop
    def updateChargePlot(self):
        # Retrieve charging data
        self.timePoint = time.time() - self.beginChargeTime
        voltageLoadPoint = self.readSensor(inputPinDefaults['Load Voltage'])
        voltagePSPoint = self.readSensor(inputPinDefaults['Power Supply Voltage'])
        currentLoadPoint = self.readSensor(inputPinDefaults['Load Current'])
        currentPSPoint = self.readSensor(inputPinDefaults['Power Supply Current'])

        self.chargeTime = np.append(self.chargeTime, self.timePoint)
        self.chargeVoltageLoad = np.append(self.chargeVoltageLoad, voltageLoadPoint)
        self.chargeVoltagePS = np.append(self.chargeVoltagePS, voltagePSPoint)
        self.chargeCurrentLoad = np.append(self.chargeCurrentLoad, currentLoadPoint)
        self.chargeCurrentPS = np.append(self.chargeCurrentPS, currentPSPoint)

        # Plot the new data
        self.replotCharge()

        # Voltage reaches a certain value of chargeVoltage to begin countown clock
        if voltagePSPoint >= chargeVoltageFraction * self.chargeVoltage * 1000:
            # Start countdown only once
            if not self.countdownStarted:
                self.countdownTimeStart = time.time()
                self.charged = True
                self.countdownStarted = True

            # Time left before discharge
            self.countdownTime = self.holdChargeTime - (time.time() - self.countdownTimeStart)

            # Set countdown time to 0 seconds once discharged
            if self.countdownTime <= 0.0:
                self.discharge()

        # Also update the labels with time
        self.updateLabels()

        # Loop through this function again continuously while charging
        if self.charging == True:
            self.after(int(1000 / refreshRate), self.updateChargePlot)

    def resetChargePlot(self):
        # Set time and voltage to empty array
        self.chargeTime = np.array([])
        self.chargeVoltageLoad = np.array([])
        self.chargeVoltagePS = np.array([])
        self.chargeCurrentLoad = np.array([])
        self.chargeCurrentPS = np.array([])

        # Also need to reset the twinx axis
        self.chargeCurrentAxis.relim()
        self.chargeCurrentAxis.autoscale_view()

        self.replotCharge()

    def resetDischargePlot(self):
        # Set time and voltage to empty array
        self.dischargeTime = np.array([])
        self.dischargeVoltageLoad = np.array([])
        self.dischargeCurrentLoad = np.array([])

        # Also need to reset the twinx axis
        self.dischargeCurrentAxis.relim()
        self.dischargeCurrentAxis.autoscale_view()

        self.replotDischarge()

    def reset(self):
        # Clear all user inputs
        self.serialNumberEntry.delete(0, 'end')
        self.chargeVoltageEntry.delete(0, 'end')
        self.holdChargeTimeEntry.delete(0, 'end')

        # Reset all boolean variables, time, and checklist
        self.charged = False
        self.chargePress = False
        self.discharged = False
        self.userInputsSet = False
        self.timePoint = 0
        self.countdownStarted = False
        self.checklist_Checkbuttons = {}
        self.updateLabels()

        # Reset plots
        self.resetChargePlot()
        self.resetDischargePlot()

        # Disable all buttons except for save and help, if logged in
        self.disableButtons()
        if self.loggedIn:
            self.saveLocationButton.configure(state='normal', relief='raised')

    # Popup window for help
    def help(self):
        helpName = 'Help'
        helpWindow = MessageWindow(self, helpName, helpText)

        helpWindow.wait_window()

# Class for inserting plots into tkinter frames
class CanvasPlot(ttk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.fig, self.ax = plt.subplots(constrained_layout=True)
        self.fig.patch.set_facecolor(defaultbg)
        self.line, = self.ax.plot([],[]) #Create line object on plot
        # Function calls to insert figure onto canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(expand=1, fill=tk.BOTH)

    def update(self):
        #update graph
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

# Class for generating popup windows
class MessageWindow(tk.Toplevel):
    def __init__(self, master, name, text):
        super().__init__(master)
        # Bring pop up to the center and top
        master.eval(f'tk::PlaceWindow {str(self)} center')
        self.attributes('-topmost', True)
        self.title(name)

        self.maxWidth = 2000
        self.maxHeight = 2000
        self.maxsize(self.maxWidth, self.maxHeight)

        # Initialize okay button to False
        self.OKPress = False

        # Create two frames, one for the text, and the other for buttons on the bottom
        self.topFrame = tk.Frame(self)
        self.bottomFrame = tk.Frame(self)

        self.topFrame.pack(side='top')
        self.bottomFrame.pack(side='bottom')

        # Destroy window and set value of okay button to True
        def OKPress():
            self.OKPress = True
            self.destroy()

        # Create and place message and okay button
        self.message = tk.Message(self.topFrame, width=topLevelWidth, text=text, **text_opts)
        self.OKButton = tk.Button(self.bottomFrame, text='Okay', command=OKPress, **button_opts)

        self.message.pack(fill='both')
        self.OKButton.pack(side='left')

if __name__ == "__main__":
    app = MainApp()
    app.eval('tk::PlaceWindow . center')
    app.loginWindow.attributes('-topmost', True)
    app.eval(f'tk::PlaceWindow {str(app.loginWindow)} center')
    app.mainloop()
