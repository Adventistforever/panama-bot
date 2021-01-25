import discord
from discord.ext import commands

import dbm # special message triggers
PREFIX = "p!"
bot = commands.Bot(command_prefix=PREFIX)
import magic_log
import asyncio
import os 
import shutil
import sys # to restart the bot
import traceback # because why not
import time # cooldown
import random # random

from blitzdb import Document
from blitzdb import FileBackend
import ftputil
db = FileBackend("./db", {'serializer_class': 'json'})


class ServerSettings(Document):
	class Meta(Document.Meta):
		primary_key = 'guild_id' #use the guild_id of the author as the primary key

class BankAccount(Document):
	class Meta(Document.Meta):
		collection = 'accounts'

class Item(Document):
	class Meta(Document.Meta):
		collection = 'items'



@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

lock = False
@bot.event
async def on_message(message):
	global lock
	l = magic_log.Print()
	ml = magic_log.MessageLog()
	l.log(message.content)

	server = message.guild
	channel = message.channel
	author = message.author
	text = message.content
	mentions = message.mentions
	ml.set_channel(channel)
	if (author.id == bot.user.id):
		l.force_p("oh, it's me.")
		return
		
	if (lock):
		l.force_p("cooldown")
		return
	
	try:
		param = db.get(ServerSettings,{'guild_id' : server.id})
	except Document.DoesNotExist:
		param = ServerSettings(
		{"guild_id":server.id,
		"currency":"💰",
		"prefix":"pan",
		"default_amount":10,
		"gain":10,
		"variation":20,
		"cooldown":30
		},backend=db)
		param.save()
		db.commit()

	
	async def ping(text):
		await ml.log("teehee !")
		await ml.log(author.permissions_in(channel))
		
	async def restart(text):
		await ml.log("kk, hold on!")
		os.execv(sys.executable, ['python'] + sys.argv)
	
	async def money(text):
		param = db.get(ServerSettings,{'guild_id' : server.id})
		try:
			account = db.get(BankAccount,{'guild_id' : server.id, 'user_id' : author.id})
			l.log(account)
			account.save()
		except Document.DoesNotExist:
			await ml.log("Welcome to the economy !")
			account = BankAccount({
				"guild_id":server.id,
				"user_id":author.id,
				"amount":int(param.default_amount),
				"last_update":time.time()
			},backend=db)
			account.last_update = time.time()
			account.save()
			l.log(account)
		await ml.log("You have {1.currency}{0.amount}".format(account,param))
		
	async def money_other(text):
		param = db.get(ServerSettings,{'guild_id' : server.id})
		try:
			account = db.get(BankAccount,{'guild_id' : server.id, 'user_id' : message.mentions[0].id})
			l.log(account)
			await ml.log("They have {1.currency}{0.amount}".format(account,param))
		except Document.DoesNotExist:
			await ml.log("They don't have an account yet.")
	
	async def help(text):
		param = db.get(ServerSettings,{'guild_id' : server.id})
		await ml.log("""
```YOU GET MONEY FROM CHATTING HERE.```
```BASICS```
**Check how rich you are** : `{0.prefix} me`
**Check how rich someone is** : `{0.prefix} see @someone`
**Check if bot is online** : `{0.prefix} ping`
**Buy epic stuff** : `{0.prefix} buy`
```EXCHANGE MONEY```
**Give money** : `{0.prefix} give @someone 10`
```MOD```
**Customize your life** `{0.prefix} settings`
**Create stuff to buy, or jobs** `{0.prefix} create`
		""".format(param))
	
	async def settings(text):
		param = db.get(ServerSettings,{'guild_id' : server.id})
		await ml.log("""
```BASICS```
**Prefix** : {0.prefix}
Change with (example) : `{0.prefix} set prefix !`
**Currency** : {0.currency}
Change with (example) : `{0.prefix} set currency $`
```SETTINGS```
**Default amount** : {0.default_amount} {0.currency}
Change with (example) : `{0.prefix} set default_amount 100`
**Gain every message** : {0.gain} {0.currency}
Change with (example) : `{0.prefix} set gain 100`
**Gain variation** : {0.variation}%
Change with (example) : `{0.prefix} set variation 25`
**Cooldown (seconds)** : {0.cooldown}%
Change with (example) : `{0.prefix} set cooldown 60`
		""".format(param))
		
	async def set(text):
		if (channel is discord.DMChannel or author.guild_permissions.manage_messages):
			param = db.get(ServerSettings,{'guild_id' : server.id})
			try:
				parameters = param.attributes
				parameters[text[2]] = text[3]
				param = ServerSettings(parameters,backend=db)
				param.save()
				await ml.log("New saved value : {0}".format(text[3]))
			except Exception:
				traceback.print_exc()
				await ml.log("Nope! Example : `{0.prefix} set {1} 100`".format(param,"example"))
		else:
			await ml.log("You don't have permissions ._.")
	
	async def give(text):
		param = db.get(ServerSettings,{'guild_id' : server.id})
		account = db.get(BankAccount,{'guild_id' : server.id, 'user_id' : author.id})
		try:
			try:
				fellow_acc = db.get(BankAccount,{'guild_id' : server.id, 'user_id' : message.mentions[0].id})
			except Document.DoesNotExist :
				fellow_acc = BankAccount({
					"guild_id":server.id,
					"user_id":message.mentions[0].id,
					"amount":int(param.default_amount),
					"last_update":time.time()
				},backend=db)
				fellow_acc.save()
				l.log(fellow_acc)
			amount = [int(i) for i in text if i.isdigit()][0]
			l.force_p(amount)
			fellow_acc.amount += int(amount)
			account.amount -= int(amount)
			account.save()
			fellow_acc.save()
			await ml.log("{0}{1} goes to your buddy !".format(param.currency,amount))
		except Exception:
			traceback.print_exc()
			await ml.log("Nope! Example : `{0.prefix} give {1} {2}`. It's possible that your friend doesn't have an account yet.".format(param,"@someone","example"))
	
	async def menu(dic):
		# dic format
		# {option: description}
		await ml.log("Pick wisely. Send the option that fits you.")
		
		text = ""
		for option in dic:
			text += "\n**Send** `{0}`, for this : {1}".format(option, dic[option])
		
		await ml.log(text)
		
		def check(m):
			return author == m.author and m.content in dic
		
		try:
			msg = await bot.wait_for('message', timeout=30.0, check=check)
			return msg.content
		except asyncio.TimeoutError:
			await channel.send('bruh. too late')
			return None
	
	async def question(check,precision): # returns the message reply
		l.log("special")
		await channel.send(precision)
		try:
			msg = await bot.wait_for('message', timeout=30.0, check=check)
			return msg
		except asyncio.TimeoutError:
			await channel.send('bruh. too late')
			return None
	
	async def save(text):
		with ftputil.FTPHost("ftp-mike1844.alwaysdata.net", "mike1844_panama", os.environ["PANAMA"]) as ftp_host:
			def upload_dir(localDir, ftpDir):
				list = os.listdir(localDir)
				for fname in list:
					if os.path.isdir(localDir + fname):
						if ftp_host.exists(ftpDir + fname):
							ftp_host.rmtree(ftpDir + fname)
						ftp_host.mkdir(ftpDir + fname)
						l.log(ftpDir + fname + " is created.")
						upload_dir(localDir + fname + "/", ftpDir + fname + "/")
					else:               
						if(ftp_host.upload_if_newer(localDir + fname, ftpDir + fname)):
							l.log(ftpDir + fname + " is uploaded.")
						else:
							l.log(localDir + fname + " has already been uploaded.")
			local_dir = "./db/"
			ftp_dir = "/panama/db/"

			upload_dir(local_dir, ftp_dir)
		await ml.log("nice.")
	
	async def load(text):
		with ftputil.FTPHost("ftp-mike1844.alwaysdata.net", "mike1844_panama", os.environ["PANAMA"]) as ftp_host:
			def download_dir(ftpDir, localDir):
				list = ftp_host.listdir(ftpDir)
				for fname in list:
					if ftp_host.path.isdir(ftpDir + fname):
						if os.exists(localDir + fname)
							shutil.rmtree(localDir + fname)
						os.mkdir(localDir + fname)
						l.log(ftpDir + fname + " is created.")
						download_dir(ftpDir + fname + "/", localDir + fname + "/")
					else:               
						if(ftp_host.download_if_newer(ftpDir + fname, localDir + fname)):
							l.log(localDir + fname + " is downloaded.")
						else:
							l.log(ftpDir + fname + " has already been downloaded.")
			local_dir = "./db/"
			ftp_dir = "/panama/db/"

			download_dir(ftp_dir, local_dir)
		await ml.log("nice.")
	
	async def create(text):
		param = db.get(ServerSettings,{'guild_id' : server.id})
		account = db.get(BankAccount,{'guild_id' : server.id, 'user_id' : author.id})
		if (author.guild_permissions.manage_roles):
			try:
				pick = await menu({"1":"Item with Role","2":"Job with role (pay someone to feed a channel)"})
				await ml.log(pick)
				if (pick == "1"):
					name = (await question(lambda m : author == m.author, "Alr, What's the name ?")).content
					await ml.log(name)
					description = (await question(lambda m : author == m.author, "Describe what it's about.")).content
					await ml.log(description)
					role_id = (await question(lambda m : author == m.author, "Now, what's the role ? Ping it-")).role_mentions[0].id
					await ml.log(role_id)
					price = int((await question(lambda m : author == m.author, "Tell me the price ! (don't precise currency)")).content)
					await ml.log(price)
					item = Item({"guild_id":server.id, "creator_id": author.id, "name":name, "description": description, "role":role_id, "price":price})
					await ml.log({"guild_id":server.id, "creator_id": author.id, "name":name, "description": description, "role":role_id, "price":price})
					item.save(db)
				elif (pick == "2"):
					pass
			except Exception:
				traceback.print_exc()
				await ml.log("Nope! Example for a banana that costs 5 : `{0.prefix} banana @role 5`".format(param))
		else:
			await ml.log("You don't have permissions ._.")
	
	
	async def buy(text):
		param = db.get(ServerSettings,{'guild_id' : server.id})
		account = db.get(BankAccount,{'guild_id' : server.id, 'user_id' : author.id})
		try:
			items = db.filter(Item,{'guild_id' : server.id})
			dic = {}
			price = {}
			for item in items:
				description = ""
				description += "Price : "+param.currency+str(item.price)
				description += " : "+item.description
				dic[item.name] = description
				price[item.name] = item.price
			pick = await menu(dic)
			if pick is not None:
				print(price[item.name])
				if account.amount > price[item.name]:
					account.amount -= price[item.name]
					await author.add_roles(server.get_role(item.role))
					account.save()
					db.commit()
					await ml.log("Have fun with your "+item.name+" ! You got the role now :flushed:")
				else:
					await ml.log("You don't have enough money for this ;-; Be more active in the server !")
		except Exception:
			traceback.print_exc()
			await ml.log("smh".format(param))
	
	
	async def default(text):
		await ml.log("Command doesn't exist. Use {0} help.".format(param.prefix))
	
	if (text.startswith(param.prefix)):
		
		default_commands = {
			"ping": ping,
			"me": money,
			"see": money_other,
			"give": give,
			"help": help,
			"buy": buy,
			
			"create": create,
			"restart": restart,
			"settings": settings,
			"set": set,
			
			"save": save,
			"load": load
		}
		
		all_commands = default_commands
		
		text = text.split(" ")
		try:
			await all_commands.get(text[1],default)(text)
		except KeyError:
			await ml.log("Command doesn't exist, or our index didn't work. Contact us.")
			
	else:
		try:
			l.log({'guild_id' : server.id, 'user_id' : author.id})
			account = db.get(BankAccount,{'guild_id' : server.id, 'user_id' : author.id})
			if (time.time() - account.last_update > param.cooldown):
				gain = int(random.random()*float(param.variation)/100*float(param.gain))
				account.amount += gain
				account.last_update = time.time()
				account.save()
		except Document.DoesNotExist:
			await money(text)
	lock = False
	db.commit()

bot.run(os.environ["PANAMA"])
# PANAMA TEST https://discord.com/oauth2/authorize?&client_id=802926388235337759&scope=bot&permissions=268553216
# PANAMA https://discord.com/oauth2/authorize?&client_id=801706530536947722&scope=bot&permissions=268553216