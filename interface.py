#!/user/bin/env python
# -*- coding: utf-8 -*-

import os, re, logging, time, string
from config import configs
from db.models import Event
from db import db



VERSION = 'EFFiCiEnCy boOST Ver0.1 by Han'
TYPES = configs['types']
DATAbase = configs['db']
MAX_PAUSE = 604800 # one week

def clr():
# clear the screen
	os.system('cls')

def time_conversion(timestamp, altzone, pattern):
# input timestamp and altzone
# return a readable time string
	this_time = time.gmtime(timestamp - altzone)
	return time.strftime(pattern, this_time)

def center_string(strin,length):
	if len(strin) > length:
		tmp = strin[:length-1]
	else:
		tmp = strin
	return string.center(tmp,length)

class Interface(object):
	def display(self, current_event=None, frozen_events=[], bonus=0):
		'''
		current_event - the ID of current_event
		frozen_events - a list of frozen event IDs
		'''
		clr()
		print '+======================================'
		print '|  %s' % VERSION
		print '+======================================'
		print ''
		print '                        Current Bonus: %d' % bonus
		print 'Current Event:'
		cur_event = Event.get(current_event) if current_event else None
		if current_event is None:
			print '    [None]'
		else:
			print '    Title:     %s' % cur_event.event_title
			print '    Type:      %s' % TYPES[cur_event.event_type]
			print '    Starts @   %s' % time_conversion(cur_event.start_time,cur_event.time_zone, "%Y-%B-%d %H:%M:%S")
			delta = time.time() - cur_event.start_time
			print '    Duration:  %s' % time_conversion(delta,0, "%H:%M:%S")
		# display different due to different interfaces
		self.add_display(frozen_events)


class Welcome_Interface(Interface):
	def add_display(self, frozen_events):
		print 'Frozen Events:'
		def get_frozen_duration(pause_inter):
			# if pause_inter < MAX_PAUSE, assume it was a time-interval
			if pause_inter > MAX_PAUSE:
				return time.time() - pause_inter
			else:
				return pause_inter
			 

		if len(frozen_events) == 0:
			print '    [None]'
		for index,frozen_event in enumerate(frozen_events):
			frozen = Event.get(frozen_event)
			if frozen is None:
				print '    [None]'
				break;
			else:
				print ' %d* Title:     %s' % (index,frozen.event_title)
				print '    Type:      %s' % TYPES[frozen.event_type]
				print '    Starts @   %s' % time_conversion(frozen.start_time,frozen.time_zone, "%Y-%B-%d %H:%M:%S")
				delta = get_frozen_duration(frozen.pause_inter)
				print '    PausedFor: %s' % time_conversion(delta,0, "%H:%M:%S")

class Type_Interface(Interface):
	def add_display(self, frozen_events):
		print ''
		print 'Choose one type from listed below:'
		for index, item in enumerate(TYPES):
			print '    %d. %s' % (index,item)

class List_Interface(Interface):
	def __init__(self, cmd):
		self.cmd = cmd
		if cmd == 'lsd':
			self.dt = 86400
		elif cmd == 'lsw':
			self.dt = 604800
		elif cmd == 'lsm':
			self.dt = 2592000
		self.eariest_event = time.time() - self.dt

	def display(self, *args, **kw):
		act_time = 0
		type_time = [0 for x in range(len(TYPES))]
		clr()
		print '+======================================'
		print '| History by `%s` is listed below:' % self.cmd		
		print '+======================================'
		events = Event.find_by('start_time > %d'%self.eariest_event, order='start_time DESC')
		print '+------------------+-----------------+-----------------+----------+----------+'
		print '|   Start Time     |   Event Title   |  Event Type     | Duration |  Paused  |'		
		print '+------------------+-----------------+-----------------+----------+----------+'

		for index, history in enumerate(events):
			act_time += history.inter_time
			type_time[history.event_type] += history.inter_time
			start_time = time_conversion(history.start_time,history.time_zone, '%Y-%m-%d %H:%M')
			print '| %s | %15s | %15s | %8s | %8s |' % (start_time, center_string(history.event_title, 15), \
				center_string(TYPES[history.event_type],15),time_conversion(history.inter_time,0,'%H:%M:%S'),\
				time_conversion(history.pause_inter,0,'%H:%M:%S'))
		print '+------------------+-----------------+-----------------+----------+----------+'
		print '%d:%s / %d:%s is used during this time block!!' % (act_time/3600, time_conversion(act_time,0,'%M:%S'),\
																  self.dt/3600, time_conversion(self.dt,0,'%M:%S') )
		for index, type_name in enumerate(TYPES):			
			print '    %d:%s / %d:%s is used for %s!!' % (type_time[index]/3600, time_conversion(type_time[index],0,'%M:%S'),\
														  act_time/3600, time_conversion(act_time,0,'%M:%S'), type_name )

class Input_Interface(Interface):
	def add_display(self, frozen_events):
		pass


if __name__ == '__main__':
	logging.basicConfig(level = logging.DEBUG)
	db.create_engine(user='myblogbytranswarp', password='ThisIsPassWord', database='myblog')
	current = '001460183862935911369feb6dd4efdbc05a9ab380e469c000'
	frozen_events = ['00146018398843823564568fcee462fbe98e7128f5f4faf000', '00146018404694521f1b0e84a1645f295adff68f9a09d4c000']
	inter = Input_Interface()
	inter.display(current, frozen_events)