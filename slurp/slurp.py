#!/usr/bin/env python
#Copyright (c) 2013, Charles Duyk
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
#Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import argparse
import os
import sys
import requests
import time

DEFAULT_MESSAGE_COUNT = 100
DEFAULT_TOKEN_FILE_NAME = "token"
DEFAULT_THREAD_ID_FILE_NAME = "threadID"

tokenHelpText  = """A Facebook access token or a path to a file containing the access token on the first line. The token must have the 'mailbox_read' permission. If absent, the script searches the current directory for a file named '%s'""" % (DEFAULT_TOKEN_FILE_NAME)
threadHelpText = """ThreadID of the thread or path to a file the thread ID on the first line. If absent, the script searches the current directory for a file named '%s'""" % (DEFAULT_THREAD_ID_FILE_NAME)
numMessageHelpText = """Number of messages to retrieve. Default: %d""" % (DEFAULT_MESSAGE_COUNT)
outputHelpText="""File to write the messages to. If absent, writes to stdout"""

progress = False

class Message(object):
	def __init__(self, time, sender, text):
		super(Message, self).__init__()
		self._time = time
		self._sender = sender
		self._text = text
	
	def __str__(self):
		timeString = time.ctime(self._time)
		return u"(%s) %s: %s" % (timeString, self._sender, self._text)
	
def parseArgs():
	parser = argparse.ArgumentParser()
	parser.add_argument("-t", "--token", dest="tokenOrPath", metavar="TOKEN", default=DEFAULT_TOKEN_FILE_NAME, help=tokenHelpText);
	parser.add_argument("-i", "--threadID", dest="idOrPath", metavar="ID", default=DEFAULT_THREAD_ID_FILE_NAME, help=threadHelpText)
	parser.add_argument("-n", "--num-messages", required=False, type=int, default=DEFAULT_MESSAGE_COUNT, help=numMessageHelpText)
	parser.add_argument("-o", "--output", required=False, metavar="PATH", help=outputHelpText)
	parser.add_argument("-p", "--progress", action="store_true", help="Print progress updates to stderr")
	return parser.parse_args()

def getKey(keyOrPath):
	key = ""
	if os.path.exists(keyOrPath):
		with open(keyOrPath) as keyFile:
			key = keyFile.readline().strip()
	else:
		key = keyOrPath
	return key

def slurpMessages(threadID, token, numMessages):
	url = "https://graph.facebook.com/%s/comments" % (threadID)
	messages = []
	params = {}
	params["access_token"] = token
	params["date_format"] = 'U'
	i = 0
	while i < numMessages:
		if progress:
			sys.stderr.write("Slurping message %d\n" % i)
		response = requests.get(url, params=params)
		json = response.json()
		try:
			recieved_messages_json = json["data"]
		except KeyError as e:
			sys.stderr.write("Couldn't parse JSON response (%s) %s\n" % (e.message, json))
			break
		for message_json in recieved_messages_json:
			try:
				time = int(message_json["created_time"])
				sender = message_json["from"]["name"]
				text = message_json["message"]
				message = Message(time, sender, text)
				messages.append(message)
			except KeyError as e:
				sys.stderr.write("Coudln't parse message %d (%s) %s\n" % (i, e, message_json))
			i += 1
			if i >= numMessages:
				break
		url = json["paging"]["next"]
	return messages

def main():
	global progress
	args = parseArgs()
	progress = args.progress
	numMessages = args.num_messages
	token = getKey(args.tokenOrPath)
	threadID = getKey(args.idOrPath)
	outputFile = sys.stdout
	if args.output is not None:
		outputPath = args.output
		outputFile = open(outputPath, mode='w')
	messages = slurpMessages(threadID, token, numMessages)
	messages.sort(cmp=lambda x, y: cmp(x._time, y._time))
	output = u"\n".join(map(unicode, messages)).encode('utf-8')
	outputFile.write(output)
	outputFile.write("\n")
	outputFile.close()

if __name__ == "__main__":
	main()

