'''
by stevens4

a configuration dictionary for the Rover3 project

just as in sitzlabexpcontrol, the configuration parameters for each 
channel are stored in a dictionary of dictionaries


'''
import os
roverLogPath = os.path.relpath('logs')

poohAIColumn = 2
tiggerAIColumn = 7

analogInputsConfDict = {
    'water temperature': {
		'guiRow': 0,
		'guiColumn':3,
		'labelText': 'cooling water',
		'chamber':'both',
		'physicalChannel':'chan1',
		'scaling':1,
		'offset':0
	},	
	
    'pooh main foreline pressure': {
		'guiRow': 3,
		'guiColumn':poohAIColumn,
		'labelText': 'main foreline',
		'chamber':'pooh',
		'physicalChannel':'chan1',
		'scaling':1,
		'offset':0
	},
	
    'pooh source foreline pressure': {
		'guiRow': 2,
		'guiColumn':poohAIColumn,
		'labelText': 'source foreline',
		'chamber':'pooh',
		'physicalChannel':'chan1',
		'scaling':1,
		'offset':0
	},
	
	'tigger source foreline pressure': {
		'guiRow': 2,
		'guiColumn':tiggerAIColumn,
		'labelText': 'source foreline',
		'chamber':'tigger',
		'physicalChannel':'chan1',
		'scaling':1,
		'offset':0
	},
	
	'tigger buffer foreline pressure': {
		'guiRow': 3,
		'guiColumn':tiggerAIColumn,
		'labelText': 'buffer foreline',
		'chamber':'tigger',
		'physicalChannel':'chan1',
		'scaling':1,
		'offset':0
	},
	
    'tigger main foreline pressure': {
		'guiRow': 4,
		'guiColumn':tiggerAIColumn,
		'labelText': 'main foreline',
		'chamber':'tigger',
		'physicalChannel':'chan1',
		'scaling':1,
		'offset':0
	}
}


poohControlsColumn = 0
tiggerControlsColumn = 6 

digitalOutputsConfDict = {
    'pooh source/buffer cooling water': {
		'guiRow': 6,
		'guiColumn':poohControlsColumn,
		'labelText': 'source/buffer cooling water',
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
