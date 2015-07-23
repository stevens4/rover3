'''
by stevens4

a configuration dictionary for the Rover3 project

just as in sitzlabexpcontrol, the configuration parameters for each 
channel are stored in a dictionary of dictionaries


'''
import os
roverLogPath = os.path.relpath('logs')

# GUI Constants
DOcontrolStartRow = 5
poohAIColumn = 1
tiggerAIColumn = 6
poohControlsColumn = 0
tiggerControlsColumn = 6 

# special pin numbers
doClockPinNumber = 4
powerSensePinNumber = 26

# specific parameters for A2D chips
SAMPLE_RATES = [8, 16, 32, 64, 128, 250, 475, 860] #Hz
RANGES = [6.144, 4.096, 2.048, 1.024, 0.512, 0.256] # +/- max volts

analogInputsConfDict = {
    'water temperature': {
        'connectionType': 'diff',
        'guiRow': 0,
        'guiColumn':3,
        'labelText': 'cooling water',
        'chamber':'both',
        'i2cAddress':0x48,
        'physicalChannel':(2,3),  #actual: 
        'readOrder':0,
        'gainFactor':RANGES[5]*1000.,
        'sampleRate':SAMPLE_RATES[7],
        'mappingStyle':'poly', # to map x as a polynomial or exponential. e.g. f(x) = A*x or A^x
        'mapParams':(-32*(5./9.),100*(5./9.),0,0,0), #coeffecients for mapping function starting w/ zeroth order
        'mappedUnits':'C'
    },    
    
    'pooh main foreline pressure': {
        'connectionType': 'RSE',
        'guiRow': 3,
        'guiColumn':poohAIColumn,
        'labelText': 'main foreline',
        'chamber':'pooh',
        'i2cAddress':0x49,
        'physicalChannel':0, #actual: A-A0
        'readOrder':1,
        'gainFactor':RANGES[0]*1000.,
        'sampleRate':SAMPLE_RATES[7],
        'mappingStyle':'exp', # to map x as a polynomial or exponential. e.g. f(x) = A*x or A^x
        'mapParams':(.1,10), #.1*10^x
        'mappedUnits':'mTorr'
    },
    
    'pooh source foreline pressure': {
        'connectionType': 'RSE',
        'guiRow': 2,
        'guiColumn':poohAIColumn,
        'labelText': 'source foreline',
        'chamber':'pooh',
        'i2cAddress':0x49,
        'physicalChannel':1, #actual: A-A1
        'readOrder':2,
        'gainFactor':RANGES[0]*1000.,
        'sampleRate':SAMPLE_RATES[7],
        'mappingStyle':'exp', # to map x as a polynomial or exponential. e.g. f(x) = A*x or A^x
        'mapParams':(.1,10), # .1*10^x
        'mappedUnits':'mTorr'
    },
    
    'tigger source foreline pressure': {
        'connectionType': 'RSE',
        'guiRow': 2,
        'guiColumn':tiggerAIColumn,
        'labelText': 'source foreline',
        'chamber':'tigger',
        'i2cAddress':0x49,
        'physicalChannel':2,  #actual: A-A2
        'readOrder':3,
        'gainFactor':RANGES[0]*1000.,
        'sampleRate':SAMPLE_RATES[7],
        'mappingStyle':'poly', # to map x as a polynomial or exponential. e.g. f(x) = A*x or A^x
        'mapParams':(-1.50696,76.7746,38.6482,10.1299,0), #coeffecients for mapping function starting w/ zeroth order
        'mappedUnits':'mTorr'
    },
    
    'tigger buffer foreline pressure': {
        'connectionType': 'RSE',
        'guiRow': 3,
        'guiColumn':tiggerAIColumn,
        'labelText': 'buffer foreline',
        'chamber':'tigger',
        'i2cAddress':0x48,
        'physicalChannel':0,   #actual: B-A0
        'readOrder':4,
        'gainFactor':RANGES[0]*1000.,
        'sampleRate':SAMPLE_RATES[7],
        'mappingStyle':'poly', # to map x as a polynomial or exponential. e.g. f(x) = A*x or A^x
        'mapParams':(-1.50696,76.7746,38.6482,10.1299,0), #coeffecients for mapping function starting w/ zeroth order
        'mappedUnits':'mTorr'
    },
    
    'tigger main foreline pressure': {
        'connectionType': 'RSE',
        'guiRow': 4,
        'guiColumn':tiggerAIColumn,
        'labelText': 'main foreline',
        'chamber':'tigger',
        'i2cAddress':0x48,
        'physicalChannel':1,    #actual: B-A1
        'readOrder':5,
        'gainFactor':RANGES[0]*1000.,
        'sampleRate':SAMPLE_RATES[7],
        'mappingStyle':'poly', # to map x as a polynomial or exponential. e.g. f(x) = A*x or A^x
        'mapParams':(-1.50696,76.7746,38.6482,10.1299,0), #coeffecients for mapping function starting w/ zeroth order
        'mappedUnits':'mTorr'
    }
}


digitalOutputsConfDict = {
    'pooh source-buffer cooling water': {
        'guiRow': DOcontrolStartRow + 1,
        'guiColumn':poohControlsColumn,
        'labelText': 'source-buffer cooling water',
        'chamber':'pooh',
        'physicalChannel':18
    },

    'pooh main roughing': {
        'guiRow': DOcontrolStartRow + 3,
        'guiColumn':poohControlsColumn,
        'labelText': 'main roughing pump',
        'chamber':'pooh',
        'physicalChannel':23
    },

    'pooh source roughing pump': {
        'guiRow': DOcontrolStartRow + 2,
        'guiColumn':poohControlsColumn,
        'labelText': 'source roughing pump',
        'chamber':'pooh',
        'physicalChannel':24
    },

    'pooh diffusion pumps': {
        'guiRow': DOcontrolStartRow + 5,
        'guiColumn':poohControlsColumn,
        'labelText': 'source diffusion pumps',
        'chamber':'pooh',
        'physicalChannel':25
    },
    
    'pooh main gate valve': {
        'guiRow': DOcontrolStartRow + 6,
        'guiColumn':poohControlsColumn,
        'labelText': 'main gate valve',
        'chamber':'pooh',
        'physicalChannel':12
    },
    
    'pooh main foreline valve': {
        'guiRow': DOcontrolStartRow + 4,
        'guiColumn':poohControlsColumn,
        'labelText': 'main foreline valve',
        'chamber':'pooh',
        'physicalChannel':16
    },
    

    
    

    
    ################# BEGIN TIGGER ######################

    'tigger spare': {
        'guiRow': DOcontrolStartRow + 7,
        'guiColumn':tiggerControlsColumn,
        'labelText': 'spare',
        'chamber':'tigger',
        'physicalChannel':17 
    },
    
    'tigger water valve': {  
        'guiRow': DOcontrolStartRow + 1,
        'guiColumn':tiggerControlsColumn,
        'labelText': 'water valve',
        'chamber':'tigger',
        'physicalChannel':27
    },

    'tigger diffusion pumps': {
        'guiRow': DOcontrolStartRow + 5,
        'guiColumn':tiggerControlsColumn,
        'labelText': 'diffusion pumps',
        'chamber':'tigger',
        'physicalChannel':22
    },

    'tigger buffer foreline valve': {
        'guiRow': DOcontrolStartRow + 3,
        'guiColumn':tiggerControlsColumn,
        'labelText': 'buffer foreline valve',
        'chamber':'tigger',
        'physicalChannel':5
    },
    
    'tigger main gate valve': {
        'guiRow': DOcontrolStartRow + 6,
        'guiColumn':tiggerControlsColumn,
        'labelText': 'main gate valve',
        'chamber':'tigger',
        'physicalChannel':6
    },

    'tigger source foreline valve': {
        'guiRow': DOcontrolStartRow + 2,
        'guiColumn':tiggerControlsColumn,
        'labelText': 'source foreline valve',
        'chamber':'tigger',
        'physicalChannel':13
    },
        
    'tigger main foreline valve': {
        'guiRow': DOcontrolStartRow + 4,
        'guiColumn':tiggerControlsColumn,
        'labelText': 'main foreline valve',
        'chamber':'tigger',
        'physicalChannel':19
    }
}
'''
'tigger detector gauge': {
    'guiRow': DOcontrolStartRow + 1,
    'guiColumn':tiggerControlsColumn,
    'labelText': 'main detector gauge',
    'chamber':'tigger',
    'physicalChannel':17 
},
'''
