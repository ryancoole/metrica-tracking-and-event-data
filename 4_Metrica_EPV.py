#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data can be found at: https://github.com/metrica-sports/sample-data

@author: Ryan Coole (@RyanCoole96)
"""

import Metrica_IO as mio
import Metrica_Viz as mviz
import Metrica_Velocities as mvel
import Metrica_PitchControl as mpc
import Metrica_EPV as mepv

#Set up initial path to data and look at sample match 2
DATADIR = '/Users/ryan_/OneDrive/Desktop/LaurieOnTracking-master'
game_id = 2

#Read in the event data
events = mio.read_event_data(DATADIR,game_id)

#Read in tracking data
tracking_home = mio.tracking_data(DATADIR,game_id,'Home')
tracking_away = mio.tracking_data(DATADIR,game_id,'Away')

#Convert positions from metrica units to meters (note change in Metrica's coordinate system since the last lesson)
tracking_home = mio.to_metric_coordinates(tracking_home)
tracking_away = mio.to_metric_coordinates(tracking_away)
events = mio.to_metric_coordinates(events)

#Reverse direction of play in the second half so that home team is always attacking from right->left
tracking_home,tracking_away,events = mio.to_single_playing_direction(tracking_home,tracking_away,events)

#Calculate player velocities
tracking_home = mvel.calc_player_velocities(tracking_home,smoothing=True,filter_='moving_average')
tracking_away = mvel.calc_player_velocities(tracking_away,smoothing=True,filter_='moving_average')

""" *** UPDATES TO THE MODEL: OFFSIDES """
#First get pitch control model parameters
params = mpc.default_model_params()
#Find goalkeepers for offside calculation
GK_numbers = [mio.find_goalkeeper(tracking_home),mio.find_goalkeeper(tracking_away)]

""" *** GET EPV SURFACE **** """
home_attack_direction = mio.find_playing_direction(tracking_home,'Home') # 1 if shooting left-right, else -1
EPV = mepv.load_EPV_grid(DATADIR+'/EPV_grid.csv')
#Plot the EPV surface
mviz.plot_EPV(EPV,field_dimen=(106.0,68),attack_direction=home_attack_direction)

#Plot event leading up to first away team goal
mviz.plot_events( events.loc[820:823], color='k', indicators = ['Marker','Arrow'], annotate=True )

#Calculate value-added for assist and plot expected value surface
event_number = 822 #Away team first goal
EEPV_added, EPV_diff = mepv.calculate_epv_added( event_number, events, tracking_home, tracking_away, GK_numbers, EPV, params)
PPCF,xgrid,ygrid = mpc.generate_pitch_control_for_event(event_number, events, tracking_home, tracking_away, params, GK_numbers, field_dimen = (106.,68.,), n_grid_cells_x = 50, offsides=True)
fig,ax = mviz.plot_EPV_for_event( event_number, events,  tracking_home, tracking_away, PPCF, EPV, annotate=True, autoscale=True )
fig.suptitle('Pass EPV added: %1.3f' % EEPV_added, y=0.95 )
mviz.plot_pitchcontrol_for_event( event_number, events,  tracking_home, tracking_away, PPCF, annotate=True)

""" **** calculate value-added for all passes **** """

#First get all shots
shots = events[events['Type']=='SHOT']
home_shots = shots[shots['Team']=='Home']
away_shots = shots[shots['Team']=='Away']
#Get all  passes
home_passes = events[ (events['Type'].isin(['PASS'])) & (events['Team']=='Home') ]
away_passes = events[ (events['Type'].isin(['PASS'])) & (events['Team']=='Away') ]

#Home team value added
home_pass_value_added = []
for i,pass_ in home_passes.iterrows():
    EEPV_added, EPV_diff = mepv.calculate_epv_added( i, events, tracking_home, tracking_away, GK_numbers, EPV, params)
    home_pass_value_added.append( (i,EEPV_added,EPV_diff ) )
    
#Away team value added
away_pass_value_added = []
for i,pass_ in away_passes.iterrows():
    EEPV_added, EPV_diff = mepv.calculate_epv_added( i, events, tracking_home, tracking_away, GK_numbers, EPV, params)
    away_pass_value_added.append( (i,EEPV_added,EPV_diff ) )
    
home_pass_value_added = sorted(home_pass_value_added, key = lambda x: x[1], reverse=True)  
away_pass_value_added = sorted(away_pass_value_added, key = lambda x: x[1], reverse=True)  
    
print("Top 5 home team passes by expected EPV-added")
print(home_pass_value_added[:5])
print("Top 5 away team passes by expected EPV-added")
print(away_pass_value_added[:5])

event_number = 1753 #Home team assist to header off target
EEPV_added, EPV_diff = mepv.calculate_epv_added( event_number, events, tracking_home, tracking_away, GK_numbers, EPV, params)
PPCF,xgrid,ygrid = mpc.generate_pitch_control_for_event(event_number, events, tracking_home, tracking_away, params, GK_numbers, field_dimen = (106.,68.,), n_grid_cells_x = 50, offsides=True)
fig,ax = mviz.plot_EPV_for_event( event_number, events,  tracking_home, tracking_away, PPCF, EPV, annotate=True )
fig.suptitle('Pass EPV added: %1.3f' % EEPV_added, y=0.95 )
mviz.plot_pitchcontrol_for_event( event_number, events,  tracking_home, tracking_away, PPCF, annotate=True )

event_number = 1663 #Away team assisst to blocked shot
EEPV_added, EPV_diff = mepv.calculate_epv_added( event_number, events, tracking_home, tracking_away, GK_numbers, EPV, params)
PPCF,xgrid,ygrid = mpc.generate_pitch_control_for_event(event_number, events, tracking_home, tracking_away, params, GK_numbers, field_dimen = (106.,68.,), n_grid_cells_x = 50, offsides=True)
fig,ax = mviz.plot_EPV_for_event( event_number, events,  tracking_home, tracking_away, PPCF, EPV, annotate=True )
fig.suptitle('Pass EPV added: %1.3f' % EEPV_added, y=0.95 )
mviz.plot_pitchcontrol_for_event( event_number, events,  tracking_home, tracking_away, PPCF, annotate=True )

#Retaining possession
event_number = 195
EEPV_added, EPV_diff = mepv.calculate_epv_added( event_number, events, tracking_home, tracking_away, GK_numbers, EPV, params)
PPCF,xgrid,ygrid = mpc.generate_pitch_control_for_event(event_number, events, tracking_home, tracking_away, params, GK_numbers, field_dimen = (106.,68.,), n_grid_cells_x = 50, offsides=True)
fig,ax = mviz.plot_EPV_for_event( event_number, events,  tracking_home, tracking_away, PPCF, EPV, annotate=True )
fig.suptitle('Pass EPV added: %1.3f' % EEPV_added, y=0.95 )
mviz.plot_pitchcontrol_for_event( event_number, events,  tracking_home, tracking_away, PPCF, annotate=True )


'''
 # find maximum possible EPV-added for all home team passes (TAKES A WHILE TO RUN!)
maximum_EPV_added = []
for i,row in home_passes.iterrows():
    print( 'Event %d' % (i) )
    EEPV_added, EPV_diff = mepv.calculate_epv_added( i, events, tracking_home, tracking_away, GK_numbers, EPV, params)
    max_EEPV_added, target = mepv.find_max_value_added_target( i, events, tracking_home, tracking_away, GK_numbers, EPV, params )
    maximum_EPV_added.append( (i,max_EEPV_added,EEPV_added,EPV_diff))

# sort by the difference between maximum value-added and value-added for the actual pass that was made
# note: some values may be slightly negative because of how the maximum value-added search is performed over a grid
maximum_EPV_added = sorted(maximum_EPV_added,key = lambda x: x[1]-x[2], reverse=True)
'''

#Assist example
event_number = 1680
PPCF,xgrid,ygrid = mpc.generate_pitch_control_for_event(event_number, events, tracking_home, tracking_away, params, GK_numbers, field_dimen = (106.,68.,), n_grid_cells_x = 50, offsides=True)
fig,ax = mviz.plot_EPV_for_event( event_number, events,  tracking_home, tracking_away, PPCF, EPV, annotate=True, autoscale=True, contours=True )

#Cross-field passes
examples = [403,68,829]
for event_number in examples:
    PPCF,xgrid,ygrid = mpc.generate_pitch_control_for_event(event_number, events, tracking_home, tracking_away, params, GK_numbers, field_dimen = (106.,68.,), n_grid_cells_x = 50, offsides=True)
    fig,ax = mviz.plot_EPV_for_event( event_number, events,  tracking_home, tracking_away, PPCF, EPV, annotate=True, autoscale=True, contours=True )
       