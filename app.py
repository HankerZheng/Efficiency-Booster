import os, re, time, logging, json, sys, msvcrt

from multiprocessing import Process

from interface import Welcome_Interface, Type_Interface, List_Interface, Input_Interface, TYPES, MAX_PAUSE
from config import configs
from db.models import Event
from db import db
from backup_script import backup_from_file

SCORES = configs['scores']
DATAbase = configs['db']
_REFRESH_TIME = 1 # in seconds
_RE_LS = re.compile('^ls[dwm]$')

class ExitApp(Exception):
	def __init__(self):
		super(ExitApp, self).__init__()

class App_Engine(object):
	def __init__(self, current_event, frozen_events, bonus):
		self.current_event = current_event
		self.frozen_events = frozen_events
		self.bonus = bonus
		self.interface = Welcome_Interface()

	def show_UI(self):
		self.interface.display(self.current_event, self.frozen_events, self.bonus)

	def run(self):
		while True:
			try:
				self.show_UI()
				if isinstance(self.interface, List_Interface):
					time.sleep(1000)
				time.sleep(_REFRESH_TIME)
			except KeyboardInterrupt:
				while msvcrt.kbhit():
					msvcrt.getch()
				if isinstance(self.interface, List_Interface):
					self.interface = Welcome_Interface()
				else:
					self.cmd_handler(raw_input('>>> '))

	def cmd_handler(self, cmd):
		'''
		according to input 'cmd', choose handler functions.
		This func returns a Interface Type variable
		'''
		if cmd == 's' or cmd == 'start':
			self.start_handler()
		elif cmd == 'b' or cmd == 'backup':
			self.backup_handler()
		elif cmd == 'p' or cmd =='pause':
			self.pause_handler()
		elif cmd == 'r' or cmd == 'resume':
			self.resume_handler()
		elif cmd == 'e' or cmd == 'end':
			self.end_handler()
		elif cmd == 'q' or cmd == 'quit':
			self.quit_handler()
		elif cmd == 'exit':
			self.exit_handler()
		elif _RE_LS.match(cmd):
			self.list_handler(cmd)

	def start_handler(self):
		'''
		* enter Type_Interface
		* create a new event entry in DataBase with TITLE and TYPE
		  list TYPE table while creating (add_display)
		* go back to WELCOME interface
		* display it as CURRENT EVENTS
		* if there is already an event in process, automatically call pause first
		'''
		if self.current_event is not None:
			# there is a CURRENT_EVENT, pause it first
			self.pause_handler()
		self.interface = Type_Interface()
		self.show_UI()
		num = ''
		while not (num.isdigit() and int(num) < len(TYPES)):
			num = raw_input('Please choose one frozen event.\n>>> ')
		num = int(num)
		event_type = num
		event_title = raw_input('Input the title for the event\n>>> ')
		event = Event(event_type=event_type,event_title=event_title)
		event.insert()
		self.current_event = event.event_id
		self.interface = Welcome_Interface()

	def backup_handler(self):
		"""
		* wait the backup file
		* create events and insert them into the database's table
		"""
		file_name = raw_input('Input the title for the event\n>>> ')
		import os.path
		if not os.path.isfile(file_name):
			pause = raw_input("File doesn't exist, press any key to continue...")
			return
		try:
			backup_from_file(file_name)
		except BaseException, e:
			print "Backup failed, press any key to continue..."
			raise e
			return
		pause = raw_input("Backup successed, press any key to continue...")


	def pause_handler(self):
		'''
		* move current_event into frozen_events lists, current_event = None
		* update pause_inter in DataBase to time.time()
			+ read pause_inter first if larger than MAX_PAUSE, assume it as timestamp
										smaller than MAX_PAUSE, assume it as time_interval
			+ renew the pause_inter to 'timestamp' or 'time.time() - time_interval'
		* go back to WELCOME interface
		'''
		if self.current_event is None:
			return
		self.frozen_events.append(self.current_event)
		event, self.current_event = Event.get(self.current_event), None
		if event.pause_inter < MAX_PAUSE:
			event.pause_inter = time.time() - event.pause_inter
			event.update()
		if not isinstance(self.interface, Welcome_Interface):
			self.interface = Welcome_Interface()

	def resume_handler(self):
		'''
		* choose a frozen event to be melt - index is showed in FROZEN EVENTS
		* set pause_inter to time-interval form
		* move the chosen event into current_event
		'''
		if not (self.current_event is None):
			return
		num = ''
		while not (num.isdigit() and int(num) < len(self.frozen_events)):
			num = raw_input('Please choose one frozen event.\n>>> ')
		num = int(num)
		event = Event.get(self.frozen_events[num])

		if event.pause_inter > MAX_PAUSE:
			event.pause_inter = time.time() - event.pause_inter
			event.update()

		self.current_event = self.frozen_events[num]
		del self.frozen_events[num]

	def end_handler(self):
		'''
		* set end_time and inter_time (inter_time = end - start - pause_inter)
		* wait for input from user to set EVENT_CTT
		* update new data into DataBase, remove this event from current_event
		'''
		if self.current_event is None:
			return
		event = Event.get(self.current_event)
		event.end_time = time.time()
		event.inter_time = event.end_time - event.start_time - event.pause_inter
		string = raw_input('Please input the content of this event:\n>>> ').decode('GBK')
		event.event_ctt = string
		event.update()
		self.bonus += SCORES[event.event_type]
		self.current_event = None

	def quit_handler(self):
		self.interface = Welcome_Interface()

	def list_handler(self, cmd):
		self.interface = List_Interface(cmd)

	def exit_handler(self):
		raise ExitApp()

def init_app():
	'''
	1. data base initial
	2. JSON load from DATA
	'''
	db.create_engine(user=DATAbase['user'], password=DATAbase['password'], database=DATAbase['database'])
	with open('DATA', 'r') as f:
		text = f.read()
		data = json.loads(text)
	# check data read from DATA
	 # first check current
	event = Event.get(data['current']) if data['current'] else None
	if event is None:
		data['current'] = None
	 # then check frozens
	if len(data['frozen']) > 0:
		for index in xrange( len(data['frozen'])-1, -1, -1):
			event = data['frozen'][index]
			if Event.get(event) is None:
				del data['frozen'][index]
	# load data into app
	app = App_Engine(data['current'], data['frozen'], data['bonus'])
	return app

def end_app(app):
	d = dict(current=app.current_event, frozen=app.frozen_events, bonus=app.bonus)
	with open('DATA', 'w') as f:
		text = json.dumps(d)
		f.write(text)

if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG, filename='app.log')
	app = init_app()
	error = None
	try:
		app.run()
	except (KeyboardInterrupt, EOFError,ExitApp):
		print 'EOF'
		pass
	else:
		raise
	finally:
		p = Process(target=end_app, args=(app,))
		p.start()
		time.sleep(2)
		print 'Safely Exit the APP'