import discord
from discord.ext import commands

import dbm # special message triggers
PREFIX = "p!"
bot = commands.Bot(command_prefix=PREFIX)
import magic_log
import asyncio
import os # to restart the bot
import shutil
import sys # to restart the bot
import traceback # because why not
import time # cooldown
import random # random

import podoks
import ftputil
import pickle
# from blitzdb import Document
# from blitzdb import FileBackend
# db = FileBackend("./db", {'serializer_class': 'json'})
with ftputil.FTPHost("ftp-ftpmike1844.alwaysdata.net", "ftpmike1844_panama", os.environ["PANAMA"]) as ftp_host:
	acc_db = podoks.Instance.load(ftp_host,"/acc_data","account_and_server_settings")
	item_db = podoks.Instance.load(ftp_host,"/item_data","items")
	job_db = podoks.Instance.load(ftp_host,"/job_data","jobs")


cute_pics = [
"https://i.imgur.com/nNx9MYb.png",
"https://i.imgur.com/J7wk90W.png",
"https://i.imgur.com/seGAtjP.png",
"https://i.imgur.com/lhuCPTF.png",
"https://i.imgur.com/LCSTjFf.png",
"https://i.imgur.com/lEhFnGj.jpg",
"https://i.imgur.com/uDGPjmz.jpg",
"https://i.imgur.com/Vk20HsG.jpg",
"https://i.imgur.com/gxV67Ri.jpg"
]


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
		param = acc_db.get("settings",server.id)
	except podoks.NoSuchCollectionError:
		acc_db.create_collection("settings")
		param = None
	if not param :
		param = acc_db.put("settings",server.id,
		{"guild_id":server.id,
		"currency":"💰",
		"prefix":"pan",
		"default_amount":10,
		"gain":10,
		"variation":20,
		"cooldown":30
		})
		
	async def ping(text):
		await ml.log("teehee !")
		await ml.log(":pleading_face: "+random.choice(cute_pics))
		
	async def restart(text):
		await ml.log("kk, hold on!")
		os.execv(sys.executable, ['python'] + sys.argv)
	
	async def money(text):
		param = acc_db.get("settings",server.id)
		
		try:
			account = acc_db.get(server.id,author.id)
		except podoks.NoSuchCollectionError:
			acc_db.create_collection(server.id)
			account = None
		
		if not account:
			await ml.log("Your account has been created on Panama Economy. \n") # +random.choice(cute_pics))
			account = acc_db.put(server.id,author.id,{
				"guild_id":server.id,
				"user_id":author.id,
				"amount":int(param.default_amount),
				"last_update":time.time()
			})

		l.log(account)
		await ml.log("You have {1.currency}{0.amount} ! Check out `pan shop` !".format(account,param))
		
	async def money_other(text):
		param = acc_db.get("settings",server.id)
		account = acc_db.get(server.id,message.mentions[0].id)
		if not account:
			await ml.log("They don't have an account yet.")
		l.log(account)
		await ml.log("They have {1.currency}{0.amount}".format(account,param))
	
	async def help(text):
		param = acc_db.get("settings",server.id)
		await ml.log("""
```YOU GET MONEY FROM CHATTING HERE.```
```BASICS```

**Check if bot is online** : `{0.prefix} ping`

**Check how rich you are** : `{0.prefix} me`
**Check how rich someone is** : `{0.prefix} see @someone`

**Buy epic stuff** : `{0.prefix} buy`
**Accept a mission (get more quicker)** : `{0.prefix} mission`

```EXCHANGE MONEY```
**Give money** : `{0.prefix} give @someone 10`
```MOD```
**Customize your life** `{0.prefix} settings`
**Create stuff to buy, or jobs** `{0.prefix} create`
**Set the money of someone or yourself :joy:** `{0.prefix} set_money @someone`
		""".format(param))
	
	async def settings(text):
		param = acc_db.get("settings",server.id)
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
**Cooldown (seconds)** : {0.cooldown}s
Change with (example) : `{0.prefix} set cooldown 60`
		""".format(param))
		
	async def set(text):
		if (channel is discord.DMChannel or author.guild_permissions.manage_messages):
			param = acc_db.get("settings",server.id)
			try:
				param[text[2]] = text[3]
				param.save()
				await ml.log("New saved value : {0}".format(text[3]))
			except Exception:
				traceback.print_exc()
				await ml.log("Nope! Example : `{0.prefix} set {1} 100`".format(param,"example"))
		else:
			await ml.log("You don't have permissions ._.")
	
	async def give(text):
		param = acc_db.get("settings",server.id)
		account = acc_db.get(server.id, author.id)
		try:
			fellow_acc = acc_db.get(server.id, message.mentions[0].id)
			if not fellow_acc:
				fellow_acc = acc_db.put(server.id,message.mentions[0].id,{
					"guild_id":server.id,
					"user_id":author.id,
					"amount":int(param.default_amount),
					"last_update":time.time()
				})
				fellow_acc.save()
				l.force_p(fellow_acc)
			amount = [int(i) for i in text if i.isdigit()][0]
			l.force_p(amount)
			account["amount"] = account["amount"] - int(amount)
			fellow_acc["amount"] = fellow_acc["amount"] + int(amount)
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
			text += "\n~"
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
		await ml.log("nice.")
	
	async def load(text):
		await ml.log("nice.")
	
	async def set_money(text):
		param = acc_db.get("settings",server.id)
		account = acc_db.get(server.id, author.id)
		if (author.guild_permissions.manage_guild):
			try:
				fellow_acc = acc_db.get(server.id, message.mentions[0].id)
				if not fellow_acc:
					fellow_acc = acc_db.put(server.id,author.id,{
						"guild_id":server.id,
						"user_id":author.id,
						"amount":int(param.default_amount),
						"last_update":time.time()
					})
					fellow_acc.save()
					l.force_p(fellow_acc)
				amount = [int(i) for i in text if i.isdigit()][0]
				l.force_p(amount)
				fellow_acc["amount"] = int(amount)
				fellow_acc.save()
				await ml.log("{0}{1} is now their balance !".format(param.currency,amount))
			except Exception:
				traceback.print_exc()
				await ml.log("Nope! Example : `{0.prefix} give {1} {2}`. It's possible that this guy doesn't have an account yet.".format(param,"@someone","example"))
		else:
			await ml.log("You don't have permissions ._.")

	async def create(text):
		await ml.log("nice.")
		param = acc_db.get("settings",server.id)
		account = acc_db.get(server.id,author.id)
		if (author.guild_permissions.manage_roles):
			try:
				pick = await menu({"1":"Item with Role","2":"Mission with role (pay someone to feed a channel, only one job per channel)"})
				await ml.log(pick)
				if (pick == "1"):
					name = (await question(lambda m : author == m.author, "Alr, What's the name ? (ONE WORD)")).content
					await ml.log(name)
					description = (await question(lambda m : author == m.author, "Describe what it's about.")).content
					await ml.log(description)
					role_id = (await question(lambda m : author == m.author, "Now, what's the role ? Ping it-")).role_mentions[0].id
					await ml.log(role_id)
					price = int((await question(lambda m : author == m.author, "Tell me the price ! (don't precise currency)")).content)
					await ml.log(price)
					
					if not item_db.collection_exists(server.id):
						item_db.create_collection(server.id)
					item = item_db.put(server.id,name,
					{"guild_id":server.id, 
					"creator_id": author.id, 
					"name":name, 
					"description": description, 
					"role":role_id, 
					"price":price})
					await ml.log(item)
					item.save()
					
					with ftputil.FTPHost("ftp-ftpmike1844.alwaysdata.net", "ftpmike1844_panama", os.environ["PANAMA"]) as ftp_host:
						item_db.save(ftp_host,"/item_data")
				elif (pick == "2"):
					name = (await question(lambda m : author == m.author, "Alr, What's the name ? (ONE WORD)")).content
					await ml.log(name)
					description = (await question(lambda m : author == m.author, "Describe what it's about.")).content
					await ml.log(description)
					role_id = (await question(lambda m : author == m.author, "Now, what's the role ? Ping it-")).role_mentions[0].id
					await ml.log(role_id)
					channel_id = (await question(lambda m : author == m.author, "Now, what's the channel ? Mention it-")).channel_mentions[0].id
					await ml.log(channel_id)
					gain = int((await question(lambda m : author == m.author, "Tell me the gain every message ! (don't precise currency)")).content)
					await ml.log(gain)
					
					if not job_db.collection_exists(server.id):
						job_db.create_collection(server.id)
					job = job_db.put(server.id,channel_id,
					{"guild_id":server.id, 
					"creator_id": author.id, 
					"name":name, 
					"description": description, 
					"role":role_id,
					"channel":channel_id,
					"gain":gain})
					await ml.log(job)
					job.save()
					with ftputil.FTPHost("ftp-ftpmike1844.alwaysdata.net", "ftpmike1844_panama", os.environ["PANAMA"]) as ftp_host:
						job_db.save(ftp_host,"/job_data")
				
			except Exception:
				traceback.print_exc()
				await ml.log("Well there was a problem, contact us ;-;".format(param))
		else:
			await ml.log("You don't have permissions ._.")
	
	async def work(text):
		await ml.log("nice.")
		l.log(job_db)
		param = acc_db.get("settings",server.id)
		account = acc_db.get(server.id, author.id)
		try:
			jobs = job_db.get_collection(server.id)
			dic = {}
			role = {}
			for key in jobs:
				description = ""
				description += jobs[key]["description"]
				description += "... you'll be payed more to use "+server.get_channel(jobs[key].channel).mention
				dic[jobs[key].name] = description
				role[jobs[key].name] = jobs[key].role
			picked_key = await menu(dic)
			
			if picked_key is not None:
				print(role[picked_key])
				await author.add_roles(server.get_role(role[picked_key]))
				await ml.log("Have fun with your "+picked_key+" job ! You got the role now :flushed:")
		except Exception:
			traceback.print_exc()
			await ml.log("smh".format(param))
	
	async def buy(text):
		await ml.log("nice.")
		
		param = acc_db.get("settings",server.id)
		account = acc_db.get(server.id, author.id)
		try:
			items = item_db.get_collection(server.id)
			dic = {}
			price = {}
			for key in items:
				description = ""
				description += items[key].description
				description += " ; Price : "+param.currency+str(items[key].price)
				dic[key] = description
				price[key] = items[key].price
			picked_key = await menu(dic)
			
			if picked_key is not None:
				print(price[picked_key])
				if account.amount > price[picked_key]:
					account["amount"] = account.amount - price[picked_key]
					await author.add_roles(server.get_role(items[picked_key].role))
					account.save()
					await ml.log("Have fun with your "+items[picked_key].name+" ! You got the role now :flushed:")
				else:
					await ml.log("You don't have enough money for this ;-; Be more active in the server !")
		except Exception:
			traceback.print_exc()
			await ml.log("smh".format(param))
	
	async def default(text):
		await ml.log("Command doesn't exist. Use {0} help.".format(param.prefix))
	
	if (text.startswith(param.prefix)):
		
		default_commands = {
			"me": money,
			"money": money,
			"see": money_other,
			"give": give,
			"help": help,
			
			"shop": buy,
			"buy": buy,
			"mission": work,
			"job": work,
			
			"set_money":set_money,
			"set": set,
			
			"create": create,
			"restart": restart,
			"settings": settings,
			
			"ping": ping
		}
		
		all_commands = default_commands
		
		text = text.split(" ")
		await all_commands.get(text[1],default)(text)
		"""
		try:
			await all_commands.get(text[1],default)(text)
		except KeyError:
			await ml.log("Command doesn't exist, or our index didn't work. Contact us.")
		"""
			
	else:
		try:
			account = acc_db.get(server.id, author.id)
		except podoks.NoSuchCollectionError:
			acc_db.create_collection(server.id)
			account = None
			
		if not account:
			await money(account)
			account = acc_db.get(server.id, author.id)
		
		l.log("automatic gain for every message check");
		l.log(time.time())
		l.log(account.last_update)
		l.log(int(param.cooldown))
		if (time.time() - account.last_update > int(param.cooldown)):
			await ml.log("add")
			gain = int(param.gain) + int(float(param.variation)/100 * float(param.gain) * random.random() * 2  - 1)
			account["amount"] = account["amount"] + gain
			account["last_update"] = time.time()
			await ml.log(gain)
			account.save()
		
		try:
			if job_db.get(server.id,channel.id) is not None :
				job = job_db.get(server.id,channel.id)
				if server.get_role(job["role"]) in author.roles:
					account["amount"] = account["amount"] + job["gain"]
					account.save()
		except podoks.NoSuchCollectionError:
			pass

	lock = False
	with ftputil.FTPHost("ftp-ftpmike1844.alwaysdata.net", "ftpmike1844_panama", os.environ["PANAMA"]) as ftp_host:
		acc_db.save(ftp_host,"/acc_data")

bot.run(os.environ["PANAMA"])
# PANAMA TEST https://discord.com/oauth2/authorize?&client_id=802926388235337759&scope=bot&permissions=268553216
# PANAMA https://discord.com/oauth2/authorize?&client_id=801706530536947722&scope=bot&permissions=268553216
