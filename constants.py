import re
import matplotlib.lines as mlines
import datetime
from tkinter import ttk

# github website
githubSite = 'https://github.com/nickschw2/HVCapTestingApp'

# Date
today = datetime.date.today()

# NI DAQ pins
sensorName = 'PXI1Slot2'
digitalOutName = 'port0'
inputPinDefaults = {'Load Voltage': 'ai0',
'Power Supply Voltage': 'ai1',
'Load Current': 'ai2',
'Power Supply Current': 'ai3'}
outputPinDefaults = {'Power Supply Switch': 'line0',
'Load Switch': 'line1'}
inputPinOptions = ['ai0', 'ai1', 'ai2', 'ai3']
outputPinOptions = ['line0', 'line1']

# Colors
green = '#2ecc71'
yellow = '#f1c40f'
orange = '#e67e22'
red = '#e74c3c'
blue = '#3498db'
white = '#ecf0f1'
black = '#000000'
grey = '#636262'
lightGrey = '#a9a1a1'
defaultbg = '#f0f0f0'
UMDRed = '#e03a3d'

# Usernames
acceptableUsernames = ['nickschw', 'koeth', 'beaudoin', 'romero', 'rschnei4']
acceptablePasswords = ['plasma']

# Widget display constants
userInputWidth = 8
userInputPadding = 50 #pixels
loginPadding = 20 #pixels
setPinsPadding = 15 #pixels
labelPadding = 10 #pixels
buttonPadding = 50 #pixels
framePadding = 20 #pixels
plotPadding = 30 #pixels
displaySetTextTime = 1000 # ms
topLevelWidth = 30
topLevelWrapLength = 275
progressBarLength = 300

# Styles
button_opts = {'font':('Helvetica', 12), 'state':'normal'}
text_opts = {'font':('Helvetica', 12)}
entry_opts = {'font':('Helvetica', 12), 'background': lightGrey}
frame_opts = {'borderwidth': 3, 'relief': 'raised', 'padding': 12}

# Serial number format
# 3 Character Capacitor origin 3 digit serial number, e.g. LBL001
format = re.compile('.{3}\d{3}')

# Plotting constants
refreshRate = 10.0 # Hz
voltageColor = 'blue'
currentColor = UMDRed

voltageLine = mlines.Line2D([], [], color=voltageColor, linestyle='-', label='V$_{load}$')
voltageDash = mlines.Line2D([], [], color=voltageColor, linestyle='--', label='V$_{PS}$')
currentLine = mlines.Line2D([], [], color=currentColor, linestyle='-', label='I$_{load}$')
currentDash = mlines.Line2D([], [], color=currentColor, linestyle='--', label='I$_{PS}$')
chargeHandles = [voltageLine, voltageDash, currentLine, currentDash]
dischargeHandles = [voltageLine, currentLine]

# Charging constants
powerSupplyVoltage = 20e3 # V
powerSupplyResistance = 1E4 # Ohm
capacitorCapacitance = 200e-6 # Farads
RCTime = powerSupplyResistance * capacitorCapacitance
chargeVoltageLimit = 0.95 # fraction of charge state before capacitor is considered charged
maxVoltage = {'LBL': 5, 'BLU': 10, 'GRA': 50, '': 'N/A'}

checklist_steps = ['Ensure that power supply is off',
     'Ensure that the charging switch is open']
    # 'Check system is grounded',
    # 'Turn on power supply',
    # 'Enter serial number, charge voltage, and hold charge time',
    # 'Exit room and ensure nobody else is present',
    # 'Turn on HV Testing Light',
    # 'Close charging switch',
    # 'Increase voltage on power supply',
    # 'Open charging switch',
    # 'Trigger ignitron',
    # 'Save scope and video data',
    # 'Enter room, turn off power supply, and "idiot stick" all HV lines',
    # 'Turn off HV testing light']

helpText = '''
Please follow the given steps in order to correctly execute this program.\n
1. Login with username and password and press 'Login' button.\n
2. Press the 'Save Location' button and select the folder where you would like to save results. N.B. that you
are allowed to change the save location throughout use of this program.\n
3. Enter the serial number of the specific capacitor being tested in the correct format.\n
4. Enter the desired charge (in kilovolts).\n
5. Enter the desired hold time (in seconds).\n
6. Press the 'Okay' button in the top right. You should briefly see a message that these values have been 'Set!' and
can now begin the checklist.\n
7. Press 'Begin Checklist' button which will create a pop-up window that contains a series of steps.
These steps must be completed and checked before every test run. Once they are all checked, the user will
then have the ability to begin the test.\n
8. Press 'Charge' button to begin charging the capacitor. The graph on the left displays the charging state over time.
Current and voltage are measured in two places -- the power supply and the load. During charging, there should be no
current or voltage across the load as long as the load switch is open. If there is any current or voltage detected across
the load, the power supply switch will open in order to protect it. A popup window will appear indicating this fault
and asking the user if they would like to perform an 'Emergency Off' operation. This will shut off power to the switches
ensuring that any stored charge is dumped across the resistor.\n
9. Once the charge level has reached the desired charge, the power supply switch will open, disconnecting it from the
capacitor. The capacitor will hold charge at this level for the desired hold time and then discharge into the load. If
the desired voltage is not reached, the user will have to manually press the 'Discharge' button to trigger a discharge.\n
10. Once a discharge is triggered, the graph on the right will display the static discharge current and voltage provided
by the oscilloscope.\n
11. All of this data is automatically written to a save file with a unique identifier for each test run.\n
11. By pressing 'Reset' the user will clear all the fields and may begin another test.
    '''

# Saving results
columns = ['Serial Number', 'Charged Voltage (kV)', 'Hold Charge Time (s)',
    'Charge Time (s)', 'Charge Voltage PS (V)', 'Charge Voltage Load (V)', 'Charge Current PS (A)',
    'Charge Current Load (A)', 'Discharge Time (s)', 'Discharge Voltage (V)', 'Discharge Current (A)']
