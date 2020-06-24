
# <p align="center">WowBot

A simple, but really very powerful library, easily adaptizing for any bot platform

In docs, I'll show how bot works with [vk_api](https://github.com/python273/vk_api) library and [CallPoll](https://github.com/andreyzin/callpoll) library

  * [Getting started.](#getting-started)
  * [Writing your first bot](#writing-your-first-bot)
    * [A simple echo bot](#a-simple-echo-bot)
   * [Docs](#docs)
	   * [Command](#command)
		   * [Finder](#finder)
		   * [Launcher](#launcher)
		   * [Handler](#handler)
		   * [params](#params)
	   * [Pack](#pack)
	   * [Connect](#connect)
	   * [User Fields](#user-fields)
	   * [user.isactive](#user-isactive)
	   * [user.send](#user-send)
	   * [Handlers Features](#handlers-features)
	   * [Perform For Input](#perform-for-input)


## Getting started.

You can install it with (requires git):

```
$ pip install git+https://github.com/andreyzin/wowbot
```

## Writing your first bot

### A simple echo bot


Create a file called `echo_bot.py`.
Then, open the file and create an instance of the WowBot class.
```python
from wowbot import Bot, Command, Pack # imported for futher use
import vk_api
from callpoll import CallPoll

# Creating ANY api instance
session = vk_api.VkApi(token="TOKEN")
api = session.get_api()

# Transfer this api into bot 
bot = Bot(api)
```
*Note: Make sure to actually replace TOKEN with your own API Token*

Let's create a simple Command which handles incoming `Hello` text.
```python
# Firstly init finder and handler functions
# Finder function should return Bool value
def text_finder(evt, params, user, bot):
	return evt["text"] == params.get("text")
	
# Handler function shuold be Generator!
def send_message_handler(evt, params, user, bot):
	user.send(message = params["text"])
	yield 
	
#Then create command
hello_command = Command(
	(text_finder,
	{"text": "Hello"}), 
	(send_message_handler,
	{"text": "Hi!!"})
)

#And connect it to the bot
bot.connect(hello_command)
```
Finder and Handler functions __can have an arbitrary name, however, it must have four parameters (evt, params, user, bot)__.

Let's add another Command:
```python
def counter_handler(evt, params, user, bot):
	user["rating"] += 1
	user.send(message = "Input number to sum it with your rating")
	answer = yield
	number = user["rating"] + int(answer["text"])
	user.send(message = str(number))
	yield
	
counter_command = Command(
	(text_finder,
	{"text": "next"}), 
	counter_handler
)
bot.connect(counter_command)
```
Now we used here *User.fields* and tried out dialog command.

*Note: all handlers are tested in the order in which they were declared*

We now have a basic bot which we need to start
```python
app = CallPoll("SOME_SERVER")
@app.route

def  processing(data):
	bot.handle(data["object"]["message"], data["object"]["message"]["from_id"])
	return  "ok"

app.run()
```
Alright, that's it! Our source file now looks like this:
```python
from wowbot import Bot, Command, Pack # imported for futher use
import vk_api
from callpoll import CallPoll

# Creating ANY api instance
session = vk_api.VkApi(token="TOKEN")
api = session.get_api()

# Transfer this api into bot 
bot = Bot(api)

# Firstly init finder and handler functions
# Finder function should return Bool value
def text_finder(evt, params, user, bot):
	return evt["text"] == params.get("text")
	
# Handler function shuold be Generator!
def send_message_handler(evt, params, user, bot):
	user.send(message = params["text"])
	yield 
	
#Then create command
hello_command = Command(
	(text_finder,
	{"text": "Hello"}), 
	(send_message_handler,
	{"text": "Hi!!"})
)

#And connect it to the bot
bot.connect(hello_command)

def counter_handler(evt, params, user, bot):
	user["rating"] += 1
	user.send(message = "Input number to sum it with your rating")
	answer = yield
	number = user["rating"] + int(answer["text"])
	user.send(message = str(number))
	yield
	
counter_command = Command(
	(text_finder,
	{"text": "next"}), 
	counter_handler
)
bot.connect(counter_command)

app = CallPoll("SOME_SERVER")
@app.route

def  processing(data):
	bot.handle(data["object"]["message"], data["object"]["message"]["from_id"])
	return  "ok"

app.run()
```
To start the bot, simply open up a terminal and enter `python echo_bot.py` to run the bot! Test it by sending commands ('Hello' and 'next').

## Docs
Let me introduce you my library. It seems to be comlicated, but it's not at all.
First of all, You should create bot instance using
```python
bot = wowbot.Bot(api, backup_path)
```
 - **api** is API INSTANCE for platform(VK/Telegram and so on)

- **backup_path** is path where users folder and data.json are located. As default - os.path.abspath(os.getcwd()) - the path where main file is located 


The main idea is to use generator functions to handle dialog commands.
Command is a combination of **Finder, Handler and Launcher**.
**But lets start from how bot works.**
When all commands added to bot, you should send every new event in bot using 
```python
bot.handle(evt, user_id)
```
### Command
#### Finder
bot.handle searches first command, which **Finder** returned True. 
**Example of Finder**:
```python
def command_finder(evt, params, user, bot):
	return evt["text"] == "Hello World"
```
is used for command to reply to a message with text "Hello World".
**But** we can use ***params*** to make this finder universal:
```python
def command_finder(evt, params, user, bot):
	return evt["text"] == params["text"]
```
is used for command to reply to a message with text that is given in `params["text"]`.

#### Launcher
When command is found, the **Launcher** function of command is launched. It should set up command handler on user using one of theese three ways:

 1. `user.revoke(handler)` - stops all running handlers and sets up given one
 2. `user.change(handler)` - changes current running handler with given one
 3. `user.perform(handler)` - launches given handler above running handlers

**Default** launcher function:
```python
def launcher(self, evt, user, bot):
	user.revoke(self.handler(
		evt = evt,
		params = self.handler_params,
		user = user,
		bot = bot
	)
)
```
stops all running handlers and sets up given one.

#### Handler

handler is generator function. While handler is running and not interrupted by another command, on every `yield`, it recieves new event:
```python
def command_handler(evt, params, user, bot):
	# making some actions..
	# sending messages, generating something
	answer = yield # here code stops, until user sends new event
	# again some logic here, messages, so on...
	answer = yield # and again code stops and wait for new event
	# Last actions...
	...
	yield # this yield is last, it doesn't recieve any data.
```

You can use ***params*** here, as in Finder. **For example**:
```python
def command_handler(evt, params, user, bot):
	# making some actions..
	# sending messages, generating something
	answer = yield # here code stops, until user sends new event
	if answer["text"] != params["text"]:
		# Send message "Incorrect answer"
	else:
		## Send message "You're right!"
	# again some logic here, messages, so on...
	yield # this yield is last, it doesn't recieve any data.
```

Now we are ready to create basic Command!
```python
command = Command(
	finder,
	handler,
	launcher # this one isn't neccessary :)
)
```
#### params
here, finder could be **just finder function** or **tuple of finder function and some params**, that are recieved in finder as `params`

with handler, there is the same situation. It could be **just handler function** or **tuple of handler function and some params**, that are recieved in handler as `params`
### Pack
is used to unite commands. In fact, in `bot.handle()` firstly is found pack and then command is found in this pack. As default, every command is connected to default pack:
```python
Pack(
	commands = [], # Necessary, The list of commands, included in pack
	name = "default", # Necessary, Name of pack Not used yet
	description = "", # Optional, Pack description isn't used yet too
	finder = finder=lambda **x: True, # Optional, finder, like in command
	finder_params = None # Optional, params, like in command
)
```
Specifically, Finder in Pack is used to find this pack, defaultly pack could be found for any event.
If there isn't any command in this pack, matching event, the next matching Pack is checked for command to fit.

> It is better to differ commands by pack, then connecting command imidiatly to Bot
### Connect
this is function to connect command to bot(default pack) or pack:
```python
bot.connect(command) # connecting command to bot(to bot default pack)
pack.connect(command) # connecting command to pack
```
or is used to connect pack to bot:
```python
bot.connect(pack) # connecting pack to bot
```
> Dont forget to connect all commands and packs to bot!!

### User Fields
First of all, User object can have some fields. You can access them with:
```python
print(user["some_field"]) # Will print "0"
```
if user doesn't have such field, `0` is returned. You can also do:
```python
user["score"] += 1 # There was no score field, but now user score is 1
user["age"] = 15 # Now our user is teenager))
user["age"] += 1 # Happy Birthday!!
```
### user isactive
this function return True if there is any running handler. Could be used in Finder not to interrupt current handler. If user is not running Command at the moment, returns False.

### user send
this function overrides vk_api's messages.send as:
```python
user.send = lambda **kwargs: bot.api.messages.send(user_id=user_id, random_id=random.random(), **kwargs)
```
This allows to send messages to user like this:
```python
user.send(message = "Hello, world")
```
instead of this:
```python
bot.api.messages.send(user_id=user_id, random_id=random.random(), message = "Hello, world")
```

### Handlers Features
In handler, you can manage user's handlers.
 1. `user.revoke(handler)` - stops all running handlers and sets up given one if `handler` isn't None
	```python
	def command_handler(evt, params, user, bot):
		# Send message params["question"]
		answer = yield 
		if answer["text"] != params["right_answer"]:
			# Send message "Incorrect answer"
			user.revoke() # Stopping all commands
		else:
			## Send message "You're right!"
		yield
	```
 2. `user.change(handler)` - changes current running handler with given one
	```python
	def command_handler(evt, params, user, bot):
		# Send message params["question"]
		answer = yield 
		if answer["text"] != params["right_answer"]:
			user.change(
				incorrect_handler(
					evt, 
					{"answer": answer["text"]}, 
					user, 
					bot
				)
			) # stopping current handler and starting *incorrect_handler*
		else:
			## Send message "You're right!"
		yield
	```
 3. `user.perform(handler)` - launches given handler above running handlers
	```python
	def command_handler(evt, params, user, bot):
		# Send message params["question"]
		answer = yield 
		if answer["text"] != params["right_answer"]:
			# Send message "Incorrect answer"
		else:
			user.perform(
				congratulations(
					evt, 
					{}, 
					user, 
					bot
				)
			) # pausing current handler and starting *incorrect_handler*
		yield
	```
	#### Perform For Input
	There are cases when we need to collect some validated data from user, but its uncomfortable to write something like this:
	```python
	def command_handler(evt, params, user, bot):
		# Send message "Input your age"
		answer = yield
		while not answer["text"].isdigit():
			# Send message "Input your age"
			answer = yield
		user["age"] = int(answer["text"])
		
		# Send message "Input your height"
		answer = yield
		while not answer["text"].isdigit():
			# Send message "Input your height"
			answer = yield
		user["height"] = int(answer["text"])

		yield
	```
	So we can create function for numeric input to make the code easier and clear:
	```python
	def numeric_handler(evt, params, user, bot):
		# Send message params["question"]
		answer = yield
		while not answer["text"].isdigit():
			# Send message params["question"]
			answer = yield
		user.give(int(answer["text"])) # return valid data to origin handler as new event
	
	def command_handler(evt, params, user, bot):
		user.perform(numeric_handler(
					evt, 
					{"question": "Input your age"}, 
					user, 
					bot
		))
		user["age"] = yield
		
		user.perform(numeric_handler(
					evt, 
					{"question": "Input your height"}, 
					user, 
					bot
		))
		user["height"] = yield

		yield
	```	
	
