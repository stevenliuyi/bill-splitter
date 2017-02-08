from google.appengine.api import users
from google.appengine.ext import ndb
import jinja2
import webapp2
import os
import urllib
import urlparse
import splitter

JINJA_ENVIRONMENT = jinja2.Environment(
	loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions = ['jinja2.ext.autoescape'],
	autoescape = True)

DEFAULT_EVENT_NAME = 'DEFAULT_EVENT'

def init_methods(event_name = DEFAULT_EVENT_NAME):
	global event_keys
	if event_name == DEFAULT_EVENT_NAME: return
	# clear previous methods
	query = PaymentMethod.query(ancestor = event_keys[event_name])
	results = query.fetch()
	for i in results: i.put().delete()

	# add initial methods
	methods = ['cash', 'check', 'paypal']
	for i in methods:
		payment_method = PaymentMethod(parent = event_keys[event_name])
		payment_method.name = i
		payment_method.put()

def get_methods(event_name = DEFAULT_EVENT_NAME):
	query = PaymentMethod.query(ancestor = event_keys[event_name]).order(+Record.time)
	return query.fetch()

def get_names(event_name = DEFAULT_EVENT_NAME):
	query = Record.query(ancestor = event_keys[event_name]).order(+Record.time)
	records = query.fetch()
	names = []
	for i in records:
		if not i.name in names: names.append(i.name)
	return names

class Event(ndb.Model):
	name = ndb.StringProperty()
	time = ndb.DateTimeProperty(auto_now_add=True)

class PaymentMethod(ndb.Model):
	name = ndb.StringProperty()
	time = ndb.DateTimeProperty(auto_now_add=True)

class Record(ndb.Model):
	name = ndb.StringProperty()
	amount = ndb.FloatProperty()
	methods = ndb.StructuredProperty(PaymentMethod, repeated=True)
	note = ndb.StringProperty()
	time = ndb.DateTimeProperty(auto_now_add=True)

class Payment(ndb.Model):
	giver = ndb.StringProperty()
	receiver = ndb.StringProperty()
	amount = ndb.FloatProperty()
	methods = ndb.StringProperty(repeated=True)

class MainPage(webapp2.RequestHandler):
	def get(self):
		event_name = self.request.get('event', DEFAULT_EVENT_NAME)
		user = users.get_current_user()
		info = self.request.get('info')

		query = Record.query(ancestor = event_keys[event_name]).order(+Record.time)
		records = query.fetch()

		payment_methods = get_methods(event_name)
		if user:
			url = "javascript:poptastic('" + users.create_logout_url(self.request.uri) + "');"
			url_linktext = 'Logout'
			username = user.nickname()
		else:
			url = "javascript:poptastic('" + users.create_login_url(self.request.uri) +"');"
			url_linktext = 'Login'
			username = False

		template_values = {
			'records': records,
			'url': url,
			'url_linktext': url_linktext,
			'username': username,
			'event_name': event_name,
			'payment_methods': payment_methods,
			'info': info,
			'event_keys': event_keys
		}
		template = JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render(template_values))


class AddRecord(webapp2.RequestHandler):
	def post(self):
		event_name = self.request.get('event', DEFAULT_EVENT_NAME)
		record = Record(parent = event_keys[event_name])
		record.name = self.request.get('username').strip()
		record.amount = float(self.request.get('amount'))
		record.methods = []
                method_ids = self.request.get('methods', allow_multiple=True)
		for i in method_ids:
			method = PaymentMethod.get_by_id(long(i), parent = event_keys[event_name])
			record.methods.append(method)
		record.note = self.request.get('note')
		record.put()
		query_params = {
			'event': event_name,
			'info': '1'	
		}
		self.redirect('/?' + urllib.urlencode(query_params))

class DeleteRecord(webapp2.RequestHandler):
	def get(self):
		event_name = self.request.get('event', DEFAULT_EVENT_NAME)
		record_id = long(self.request.get('id'))
		record = Record.get_by_id(record_id, parent = event_keys[event_name])
                record.put().delete()
		query_params = {'event': event_name}
		self.redirect('/?' + urllib.urlencode(query_params))

class DeleteAllRecords(webapp2.RequestHandler):
	def get(self):
		event_name = self.request.get('event', DEFAULT_EVENT_NAME)
		query = Record.query(ancestor = event_keys[event_name]).order(+Record.time)
		records = query.fetch()
		for i in records: i.put().delete()
		query_params = {
			'event': event_name,
			'info': '3'
		}
		self.redirect('/?' + urllib.urlencode(query_params))

class AddEvent(webapp2.RequestHandler):
	def get(self):
		global event_keys
		event_name = self.request.get('name')
		event = Event()
		event.name = event_name
		event_keys[event_name] = event.put()
		init_methods(event_name)
		query_params = {
			'event': event_name,
			'info': '7'
		}
		self.redirect('/?' + urllib.urlencode(query_params))

class DeleteEvent(webapp2.RequestHandler):
	def get(self):
		global event_keys
		event_name = self.request.get('name')
		event_keys[event_name].delete()
		del event_keys[event_name]
		query_params = {
			'info': '8'
		}
		self.redirect('/?' + urllib.urlencode(query_params))

class EditMethods(webapp2.RequestHandler):
	def get(self):
		event_name = self.request.get('event')
		methods = self.request.get('methods')
		methods_list = methods.split(',')
		previous_methods = get_methods(event_name)
		previous_methods_list = [x.name for x in previous_methods]
		info = '5'
		for i in methods_list:
			if not i in previous_methods_list:
				payment_method = PaymentMethod(parent = event_keys[event_name])
				payment_method.name = i
				payment_method.put()
				info = '4'
		for j in previous_methods:
			if not j.name in methods_list:
				j.put().delete()
				info = '4'

		query_params = {
			'event': event_name,
			'info': info
		}
		self.redirect('/?' + urllib.urlencode(query_params))

class Calculate(webapp2.RequestHandler):
	def post(self):
		global balances
		event_name = self.request.get('event', DEFAULT_EVENT_NAME)
		tolerance = float(self.request.get('tolerance', 0))
		show = self.request.get('show', 'payments')

		# clear previous results
		query = Payment.query(ancestor = event_keys[event_name])
		results = query.fetch()
		for i in results: i.put().delete()

		query = Record.query(ancestor = event_keys[event_name]).order(+Record.time)
		records = query.fetch()
		bill = {}
		if len(records) == 0:
			query_params = {
				'event': event_name,
				'info': '6'	
			}
			self.redirect('/?' + urllib.urlencode(query_params))
			return

		payment_method_query = PaymentMethod.query( \
			ancestor = event_keys[event_name]).order(+Record.time)
		methods = payment_method_query.fetch()
		payment_methods = {}
		for i in methods:
			payment_methods[i.name] = []

		try:
			for i in records:
				if i.name in bill:
					bill[i.name] += i.amount
				else:
					bill[i.name] = i.amount
				for j in i.methods:
					if not i.name in payment_methods[j.name]:
						payment_methods[j.name].append(i.name)
		except:
			query_params = {
				'event': event_name,
				'info': '2'	
			}
			self.redirect('/?' + urllib.urlencode(query_params))
			return

		bill_list = []
		for key, value in bill.iteritems(): bill_list.append((key, value))

		balances = []
		results, balances = splitter.get_payments(bill_list, payment_methods, tolerance)
		info = ''
		if results == [None]:
			info = '10'
		elif len(results) == 0:
			info = '9'
		else:
			for i in results:
				payment = Payment(parent = event_keys[event_name])
				payment.giver = i[0]
				payment.receiver = i[1]
				payment.amount = i[2]
				payment.methods = []
				for j in i[3]: payment.methods.append(j)
				payment.put()

		query_params = {
			'event': event_name,
			'tolerance': tolerance,
			'info': info,
		}	
		if show == 'payments':
			self.redirect('/result?' + urllib.urlencode(query_params))
		elif show == 'balances':
			self.redirect('/balances?' + urllib.urlencode(query_params))

class Result(webapp2.RequestHandler):
	def get(self):
		event_name = self.request.get('event', DEFAULT_EVENT_NAME)
		tolerance = self.request.get('tolerance')
		info = self.request.get('info')
		user = users.get_current_user()
		if user:
			url = "javascript:poptastic('" + users.create_logout_url(self.request.uri) + "');"
			url_linktext = 'Logout'
			username = user.nickname()
		else:
			url = "javascript:poptastic('" + users.create_login_url(self.request.uri) +"');"
			url_linktext = 'Login'
			username = False
		query = Payment.query(ancestor = event_keys[event_name])
		results = query.fetch()

		payment_methods = get_methods(event_name)
		names = get_names(event_name)

		template_values = {
			'results': results,
			'url': url,
			'url_linktext': url_linktext,
			'username': username,
			'event_name': event_name,
			'tolerance': tolerance,
			'event_keys': event_keys,
			'payment_methods': payment_methods,
			'names': names,
			'info': info
		}
		template = JINJA_ENVIRONMENT.get_template('results.html')
		self.response.write(template.render(template_values))

class Balances(webapp2.RequestHandler):
	def get(self):
		event_name = self.request.get('event', DEFAULT_EVENT_NAME)
		tolerance = self.request.get('tolerance')
		info = self.request.get('info')
		user = users.get_current_user()
		if user:
			url = "javascript:poptastic('" + users.create_logout_url(self.request.uri) + "');"
			url_linktext = 'Logout'
			username = user.nickname()
		else:
			url = "javascript:poptastic('" + users.create_login_url(self.request.uri) +"');"
			url_linktext = 'Login'
			username = False
		query = Payment.query(ancestor = event_keys[event_name])
		results = query.fetch()

		payment_methods = get_methods(event_name)

		template_values = {
			'results': results,
			'url': url,
			'url_linktext': url_linktext,
			'username': username,
			'event_name': event_name,
			'tolerance': tolerance,
			'event_keys': event_keys,
			'balances': balances,
			'info': info
		}
		template = JINJA_ENVIRONMENT.get_template('balances.html')
		self.response.write(template.render(template_values))

event_keys = {}
event_keys[DEFAULT_EVENT_NAME] = None
events = Event.query().fetch()
for i in events:
	event_keys[i.name] = i.put()

balances = []

app = webapp2.WSGIApplication([
	('/', MainPage),
	('/add_record', AddRecord),
    ('/delete_record', DeleteRecord),
	('/delete_records', DeleteAllRecords),
	('/calc', Calculate),
	('/result', Result),
	('/balances', Balances),
	('/add_event', AddEvent),
	('/delete_event', DeleteEvent),
    ('/methods', EditMethods),
], debug = True)
