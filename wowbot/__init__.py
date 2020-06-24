import json
import os
import time

import random

class Bot:
	"""Main wowbot class"""

	def __init__(self, api, backup_path=os.path.abspath(os.getcwd())):
		self.api = api
		self.backup_path = backup_path

		self.data = {}
		self.restore_data()
		
		self.users = {}
		self.packs = [Pack([], "default")]

	def handle(self, evt, user_id):
		"""Method to handle new event"""

		user = self.get_user(user_id)

		command = self.get_command(evt, user)
		if command:
			command.launcher(evt=evt, user=user, bot=self)
		else:
			user.proceed(evt=evt)
			
		user.save()
		self.save_data()

		self.clear_stack()

	def get_user(self, user_id):
		"""Function for getting user by id. If there is no such user, borns him"""
		if user_id in self.users:
			return self.users[user_id]

		user = self.born_user(user_id, restore=True)
		self.users[user.user_id] = user
		return user

	def born_user(self, user_id, fields={}, restore=False):
		"""Borns user. Now is stupid, but it will be useful"""
		user = User(user_id, fields, restore=restore, backup_path=self.backup_path)
		user.send = lambda **kwargs: self.api.messages.send(user_id=user_id, random_id=random.random(), **kwargs)
		return user

	def get_packs(self, evt, user):
		"""Function to get pack for event"""
		for pack in self.packs[::-1]:
			if pack.explore(evt, user, self):
				yield pack
		return

	def get_command(self, evt, user):
		"""Function to get command for event in first matching pack"""
		packs = self.get_packs(evt, user)
		for pack in packs:
			command = pack.get_command(evt, user, self)
			if command:
				return command
		return None

	def connect(self, obj):
		"""Connects pack or command to bot"""
		if isinstance(obj, Command):
			self.packs[0].connect(obj)
		elif isinstance(obj, Pack):
			self.packs.append(obj)

	def clear_stack(self, expiration=5 * 60):
		"""Clears users, who haven't written for <expiration> seconds"""
		now = time.time()
		self.users = dict(filter(lambda x: x[1].last_action + expiration > now, self.users.items()))

	def save_data(self):
		with open('data.json', "w") as json_file:
			json.dump(self.data, json_file)

	def restore_data(self):
		if os.path.exists('data.json'):
			try:
				with open('data.json') as json_file:
					self.data = json.load(json_file)
			except:
				pass

class Pack:
	"""Class for commands packing"""

	def __init__(self, commands, name, finder=lambda **x: True, finder_params=None, description=None):
		self.commands = commands
		self.name = name
		self.descripton = description
		self.finder = finder
		self.finder_params = finder_params

	def connect(self, command):
		"""Connects command to the pack"""
		self.commands.append(command)

	def get_command(self, evt, user, bot):
		"""Function to get command for event in current pack"""
		for command in self.commands:
			if command.explore(evt=evt, user=user, bot=bot):
				return command

	def explore(self, evt, user, bot):
		"""Checking itself to suit event """
		return self.finder(evt=evt, params=self.finder_params, user=user, bot=bot)


class Command:
	"""Class for command"""

	def __init__(self, finder, handler, launcher = None):
		if isinstance(finder, tuple):
			self.finder = finder[0]
			self.finder_params = finder[1]
		else:
			self.finder = finder
			self.finder_params = None

		if isinstance(handler, tuple):
			self.handler = handler[0]
			self.handler_params = handler[1]
		else:
			self.handler = handler
			self.handler_params = None

		self.explore = lambda evt, user, bot: self.finder(evt=evt, params=self.finder_params, user=user, bot=bot)
		
		self.launcher = launcher or (lambda evt, user, bot: user.revoke(
			self.handler(
				evt = evt,
				params = self.handler_params,
				user = user,
				bot = bot
			)
		))

class User:
	"""User class"""

	def __init__(self, user_id, fields={}, restore=True, backup_path="/"):
		self.user_id = user_id
		self.fields = fields
		self.handlers = []
		self.last_action = time.time()

		self.backup_path = backup_path

		if restore:
			self.restore()

	def isactive(self):
		return bool(self.handlers)

	def perform(self, handler):
		self.handlers.append(handler)
		self.handlers[-1].send(None)

	def revoke(self, handler = None):
		self.handlers = []
		if handler:
			self.perform(handler)

	def change(self, handler):
		if self.handlers:
			self.handlers[-1] = handler
			self.handlers[-1].send(None)
		else:
			self.perform(handler)

	def proceed(self, evt=None):
		"""Util to work with user handler"""
		try:
			if self.handlers:
				self.handlers[-1].send(evt)
			else:
				return False

		except StopIteration:
			print(self.handlers[-1])
			del self.handlers[-1]
	
	def give(self, data):
		del self.handlers[-1]
		self.proceed(data)

	def save(self):
		"""Stores user"""
		if not os.path.exists(f'{self.backup_path}/users/'):
   			os.makedirs(f'{self.backup_path}/users')
		with open(f'{self.backup_path}/users/{self.user_id}.json', "w") as json_file:
			json.dump(self.fields, json_file)

	def restore(self):
		"""Restores user"""
		if os.path.exists(f'{self.backup_path}/users/{self.user_id}.json'):
			try:
				with open(f'{self.backup_path}/users/{self.user_id}.json') as json_file:
					self.fields = json.load(json_file)
					return
			except:
				pass

	def __delitem__(self, index):
		if index in self.fields:
			del self.fields[index]

	def __getitem__(self, index):
		return self.fields.get(index, 0)

	def get(self, index, default=None):
		return self.fields.get(index, default)

	def __setitem__(self, index, value):
		self.fields[index] = value

	def __repr__(self):
		return f"{self.fields}"