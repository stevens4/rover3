'''
by stevens4

a configuration dictionary for the Rover3 project

just as in sitzlabexpcontrol, the configuration parameters for each 
channel are stored in a dictionary of dictionaries


'''
import os
roverLogPath = os.path.relpath('logs')

poohAIColumn = 1
tiggerAIColumn = 6

SAMPLE_RATES = [8, 16, 32, 64, 128, 250, 475, 860] #Hz
RANGES = [6.144, 4.096, 2.048, 1.024, 0.512, 0.256] # +/- max volts

analogInputsConfDict = {
    'water temperature': {
        'guiRow': 0,
        'guiColumn':3,
        'labelText': 'cooling water',
        'chamber':'both',
        'i2cAddress':0x49,
        'physicalChannel':0, #actual: A3
        'readOrder':0,
        'gainFactor':RANGES[5],
        'sampleRate':SAMPLE_RATES[7],
        'mapParams':(0,1,0,0,0), #(-250.,200.,0,0,0), #coeffecients for mapping function starting w/ zeroth order
        'mappedUnits':'C'
    },    
    
    'pooh main foreline pressure': {
        'guiRow': 3,
        'guiColumn':poohAIColumn,
        'labelText': 'main foreline',
        'chamber':'pooh',
        'i2cAddress':0x49,
        'physicalChannel':1, #actual: A0
        'readOrder':1,
        'gainFactor':RANGES[0],
        'sampleRate':SAMPLE_RATES[7],
        'mapParams':(0,1,0,0,0), #coeffecients for mapping function starting w/ zeroth order
        'mappedUnits':'mTorr'
    },
    
    'pooh source foreline pressure': {
        'guiRow': 2,
        'guiColumn':poohAIColumn,
        'labelText': 'source foreline',
        'chamber':'pooh',
        'i2cAddress':0x49,
        'physicalChannel':2, #actual: A1
        'readOrder':2,
        'gainFactor':RANGES[0],
        'sampleRate':SAMPLE_RATES[7],
        'mapParams':(0,1,0,0,0), #coeffecients for mapping function starting w/ zeroth order
        'mappedUnits':'mTorr'
    },
    
    'tigger source foreline pressure': {
        'guiRow': 2,
        'guiColumn':tiggerAIColumn,
        'labelText': 'source foreline',
        'chamber':'tigger',
        'i2cAddress':0x49,
        'physicalChannel':3,  #actual: A2
        'readOrder':3,
        'gainFactor':RANGES[0],
        'sampleRate':SAMPLE_RATES[7],
        'mapParams':(0,1,0,0,0), #coeffecients for mapping function starting w/ zeroth order
        'mappedUnits':'mTorr'
    },
    
    'tigger buffer foreline pressure': {
        'guiRow': 3,
        'guiColumn':tiggerAIColumn,
        'labelText': 'buffer foreline',
        'chamber':'tigger',
        'i2cAddress':0x48,
        'physicalChannel':0,
        'readOrder':4,
        'gainFactor':RANGES[0],
        'sampleRate':SAMPLE_RATES[7],
        'mapParams':(0,1,0,0,0), #coeffecients for mapping function starting w/ zeroth order
        'mappedUnits':'mTorr'
    },
    
    'tigger main foreline pressure': {
        'guiRow': 4,
        'guiColumn':tiggerAIColumn,
        'labelText': 'main foreline',
        'chamber':'tigger',
        'i2cAddress':0x48,
        'physicalChannel':1,
        'readOrder':5,
        'gainFactor':RANGES[0],
        'sampleRate':SAMPLE_RATES[7],
        'mapParams':(0,1,0,0,0), #coeffecients for mapping function starting w/ zeroth order
        'mappedUnits':'mTorr'
    }
}


poohControlsColumn = 0
tiggerControlsColumn = 6 

digitalOutputsConfDict = {
    'pooh source-buffer cooling water': {
        'guiRow': 6,
        'guiColumn':poohControlsColumn,
        'labelText': 'source-buffer cooling water',
        'chamber':'pooh',
        'physicalChannel':18
    },    
    
    'pooh source roughing pump': {
        'guiRow': 7,
        'guiColumn':poohControlsColumn,
        'labelText': 'source roughing pump',
        'chamber':'pooh',
        'physicalChannel':23
    },
    
    'pooh main roughing': {
        'guiRow': 8,
        'guiColumn':poohControlsColumn,
        'labelText': 'main roughing pump',
        'chamber':'pooh',
        'physicalChannel':24
    },
    
    'pooh main gate valve': {
        'guiRow': 9,
        'guiColumn':poohControlsColumn,
        'labelText': 'main gate valve',
        'chamber':'pooh',
        'physicalChannel':25
    },

    'pooh main foreline valve': {
        'guiRow': 10,
        'guiColumn':poohControlsColumn,
        'labelText': 'main foreline valve',
        'chamber':'pooh',
        'physicalChannel':12
    },

    'tigger source foreline valve': {
        'guiRow': 6,
        'guiColumn':tiggerControlsColumn,
        'labelText': 'source foreline valve',
        'chamber':'tigger',
        'physicalChannel':4
    },
    
    'tigger main gate valve': {
        'guiRow': 7,
        'guiColumn':tiggerControlsColumn,
        'labelText': 'main gate valve',
        'chamber':'tigger',
        'physicalChannel':17
    },
    
    'tigger diffusion pumps': {
        'guiRow': 8,
        'guiColumn':tiggerControlsColumn,
        'labelText': 'diffusion pumps',
        'chamber':'tigger',
        'physicalChannel':27
    },

    'tigger main foreline valve': {
        'guiRow': 9,
        'guiColumn':tiggerControlsColumn,
        'labelText': 'main foreline valve',
        'chamber':'tigger',
        'physicalChannel':5
    },

    'tigger detector gauge': {
        'guiRow': 10,
        'guiColumn':tiggerControlsColumn,
        'labelText': 'main detector gauge',
        'chamber':'tigger',
        'physicalChannel':6 
    },

    'tigger water valve': {  
        'guiRow': 11,
        'guiColumn':tiggerControlsColumn,
        'labelText': 'water valve',
        'chamber':'tigger',
        'physicalChannel':13
    }
}
