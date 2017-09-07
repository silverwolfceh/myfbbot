#!/usr/bin/python
# -*- coding: utf-8 -*-
import getpass
import json
import sys
import os
from fbchat import log, Client
import requests
# No more warning
requests.packages.urllib3.disable_warnings()
# UTF-8 Message
reload(sys)
sys.setdefaultencoding('UTF8')


### SETTING START ###
ACCOUNT = "config.json"
COOKIES = "cookies.json"
DEFAULT_MSG = "Xin chào, hiện giờ tôi không online. Nếu có việc gấp xin hãy gọi điện"

USE_SIM = False
SIM_API = "http://sandbox.api.simsimi.com/request.p?key=%s&lc=en&ft=1.0&text=%s"
SIM_API_KEY = "6b4f06eb-4544-4381-be67-a911c376441d"

USE_EVE = False
EVE_API = "http://bot.evildragon.net/api.php?key=1&mode=chat&text=%s"
### SETTING END   ###

class AutoAnswer:
	@staticmethod
	def answer(msg):
		if USE_SIM: # Sim api is more priority
			response = requests.get(SIM_API % (SIM_API_KEY, msg), stream=True)
			try:
				data = json.loads(response.text)
				if data["msg"] == "OK.":
					return data['response']
				else:
					return data["msg"] # Trial is expired
			except:
				return "SIM API ERROR"
		else:
			response = requests.get(EVE_API % msg, stream=True)
			try:
				data = json.loads(response.text)
				return data['messages'][0]['text']
			except:
				return "EVE API ERROR"

class BotAnswer:
	def __init__(self, myid):
		self.author = []
		self.me = myid

	def replymessage(self, author, inputmsg):
		if not USE_SIM and not USE_EVE:
			if author not in self.author and author != self.me:
				self.author += [author]
				return DEFAULT_MSG
			else:
				return None
		else:
			if author != self.me:
				return AutoAnswer.answer(inputmsg)
			return None


class AssistantBot(Client):
	def __init__(self, fbuser, fbpass, session):
		Client.__init__(self, fbuser, fbpass, session_cookies = session, max_tries = 10, user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36")
		self.botanswer = BotAnswer(self.uid)

	def onMessage(self, author_id, message, thread_id, thread_type, **kwargs):
		self.markAsDelivered(author_id, thread_id)
		self.markAsRead(author_id)
		replymsg = self.botanswer.replymessage(author_id, message)
		if replymsg:
			self.sendMessage(replymsg, thread_id=thread_id, thread_type=thread_type)

	def on2FACode(self):
		return raw_input("Enter your 2FA code: ")

	def onLoggingIn(self, email):
		print "Try to login %s" % email


if __name__ == "__main__":
	try:
		# Load the existed session
		print "Load session file"
		session_cookies = {}
		if os.path.isfile(COOKIES):
			with open(COOKIES, "r") as f:
				session_cookies = json.loads(f.read())

		# Load account
		print "Load account file"
		fbuser = ""
		fbpass = ""
		if os.path.isfile(ACCOUNT):
			with open(ACCOUNT, "r") as f:
				data = json.loads(f.read())
				fbuser = data['Email']
				fbpass = data['Password']
		if fbuser == "" or fbpass == "":
			print "Vui long dien tai khoan"
			fbuser = raw_input("Email > ")
			fbpass = getpass.getpass()
			with open(ACCOUNT, "w") as f:
				data = {"Email": fbuser, "Password": fbpass}
				f.write(json.dumps(data))

		# Khoi tao client
		client = AssistantBot(fbuser, fbpass, session_cookies)

		# Login OK, save session
		session_cookies = client.getSession()
		with open(COOKIES, "w") as f:
			f.write(json.dumps(session_cookies))

		# Start listening to message
		print "Login success"
		client.listen()
	except:
		print "Login failed or parsing failed"
