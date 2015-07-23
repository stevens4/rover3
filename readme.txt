see documentation/Rover_3_Documentation.pdf




rover 3 functionality

need 6 AI and 12 DO, at least

hardware:
    1x raspberry pi 2 B (27 GPIO pins built in)
    2x thermocouple k-type amplifier
    1x pi breakout ribbon cable
    3x ADS1115 4chan 16b ADC  (interfaces via I2C, are stackable)
    1x power supply
    1x usb cable
    1x SD card, preloaded rasbian


analog inputs (sense):
    water thermocouple
    pooh main foreline pressure
    pooh source foreline pressure
    tigger source foreline pressure
    tigger buffer foreline pressure
    tigger main foreline pressure
    
    
digital output (relays):
    pooh water valve
    pooh source roughing
    pooh main roughing
    pooh source diffusion
    pooh main gate valve
    pooh source foreline valve
    tigger source foreline valve
    tigger main gate valve
    tigger diffusion pumps
    tigger main foreline valve
    tigger detector gauge
    tigger water valve
    
    
  
  
main features that we want:
	- real time logging of all AI & DO channels' values
		+ ability to plot history of values
		+ auto clean-up: compactify log based on age of entry
	- persist state of DIO in absence of pi power
	- automated interlocks 
		+ toggle a relay based on an AI value
		+ dispatch a message (clients, SMS) in this event
		+ add entry to status log
		+ configurable, configuration persists in absence of pi power
	- real time updating of a transcript of actions taken
	- rover client:
		+ subscribed to interlock events and DO toggle events
		+ can request current state of AI & DO
  
  
  
  
  
statusFile:
	timestamp:    [states of each DO + values of each AI]
	
transcript:
	timestamp:    [action that occurred in plain text. a capture of stdout]
  
  
  
  
  
  
  
  
  
  
  
  
  
