import json
import os
import time

import random


class Bot:
	"""Main wowbot class"""

	def __init__(self, api, backup_path=os.path.abspath(os.getcwd())):
		self.api = api
		self.backup_path = backup_path

		self.users = {}
		self.packs = [Pack([], "default")]

	def handle(self, evt, user_id):
		"""Method to handle new event"""

		user = self.get_user(user_id)

		if user.handler():
			user.handler(evt=evt)

		if not user.handler():
			command = self.get_command(evt, user)
			if command:
				user.handler(
					command.handler(evt=evt, params=command.handler_params, user=user, api=self.api, bot=self))

		user.save()
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
			return pack.get_command(evt, user, self)
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


class Pack:
	"""Class for commands packing"""

	def __init__(self, commands, name, finder=lambda **x: True, finder_params=None, descripton=None):
		self.commands = commands
		self.name = name
		self.descripton = descripton
		self.finder = finder
		self.finder_params = finder_params

	def connect(self, command):
		"""Connects command to the pack"""
		self.commands.append(command)

	def get_command(self, evt, user, bot):
		"""Function to get command for event in current pack"""
		for command in self.commands:
			if command.explore(evt=evt, user=user, bot=self):
				return command

	def explore(self, evt, user, bot):
		"""Checking itself to suit event """
		return self.finder(evt=evt, params=self.finder_params, user=user, bot=bot)


class Command:
	"""Class for command"""

	def __init__(self, finder, handler):
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


class User:
	"""User class"""

	def __init__(self, user_id, fields={}, restore=True, backup_path="/"):
		self.user_id = user_id
		self.fields = fields
		self.running_handler = None
		self.last_action = time.time()

		self.backup_path = backup_path

		if restore:
			self.restore()

	def handler(self, handler=None, evt=None):
		"""Util to work with user handler"""
		if handler:
			self.running_handler = handler
			self.running_handler.send(None)
			return True

		if evt:
			try:
				self.running_handler.send(evt)

			except StopIteration:
				self.running_handler = None

			return True

		return self.running_handler

	def save(self):
		"""Stores user"""
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