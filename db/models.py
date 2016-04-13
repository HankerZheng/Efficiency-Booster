#!/user/bin/env python
# -*- coding: utf-8 -*-


'''
Models for event
'''

import time, uuid

from orm import Model, StringField, BooleanField, FloatField, TextField, IntegerField

def next_id():
	return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

class Event(Model):
	__table__ = 'myevents'

	event_id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
	start_time = FloatField(updatable=False, default=time.time)
	end_time = FloatField(default=time.time)
	pause_inter = FloatField(default=0)
	inter_time = FloatField(default=0)
	time_zone = FloatField(default=time.altzone)
	event_title = StringField(ddl='varchar(100)')
	event_type = IntegerField(ddl='smallint', default=3)
	event_ctt = TextField(ddl='text')

if __name__ == "__main__":
	print Event().__sql__()