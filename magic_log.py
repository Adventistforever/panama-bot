class Log():
	def log(self,text):
		pass
	
	def force_p(self,text):
		print(text)

class Print(Log):
	def log(self,text):
		print(text)

class NoLog(Log) :
	def log(self,text):
		pass
		
class MessageLog(Log):
	def set_channel(self,channel):
		self.channel = channel
	
	async def log(self,text):
		await self.channel.send(text)