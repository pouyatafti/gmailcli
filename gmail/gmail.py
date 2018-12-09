from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from collections import namedtuple

import base64
import email

import os

def mime_header_item(msg, item):
	hi = msg.get(item)
	hid = email.header.decode_header(hi)[0]
	if isinstance(hid[0], bytes):
		hidec = hid[0].decode(hid[1])
	else:
		hidec = hid[0]
	return hidec

def mime_header(msg):
	items = {"From", "To", "Date", "Subject"}
	header = {item: mime_header_item(msg, item) for item in items}
	header["Date"] = email.utils.parsedate_to_datetime(header["Date"])
	header["From"] = email.utils.parseaddr(header["From"])
	header["To"] = email.utils.parseaddr(header["To"])
	
	return header

class Gmail:
	def __init__(self, creds_file="credentials.json", token_file="token.json"):
		self._SCOPES = "https://www.googleapis.com/auth/gmail.readonly"
		
		self._store = None
		self._creds = None
		self._service = None
		self.auth(creds_file, token_file)
		
	def auth(self, creds_file, token_file):
		self._store = file.Storage(token_file)
		self._creds = self._store.get()
		if not self._creds or self._creds.invalid:
			flow = client.flow_from_clientsecrets(creds_file, self._SCOPES)
			flags = tools.argparser.parse_args([])
			self._creds = tools.run_flow(flow, self._store, flags)
		self._service = build('gmail', 'v1', http=self._creds.authorize(Http()))
	
	def get_message_ids_by_query(self, q, uid="me"):
		response = self._service.users().messages().list(userId=uid, q=q).execute()
		messages = []
		if "messages" in response:
			messages.extend(response["messages"])

		while "nextPageToken" in response:
			page_token = response["nextPageToken"]
			response = service.users().messages().list(userId=uid, q=q, pageToken=page_token).execute()
			messages.extend(response["messages"])

		return [m["id"] for m in messages]

	def get_info_by_id(self, mid, uid="me"):
		message = self._service.users().messages().get(userId=uid, id=mid, format="metadata").execute()

		info = dict()
		info["id"] = mid
		info["snippet"] = message["snippet"]
		for hdr in message["payload"]["headers"]:
			info[hdr["name"]] = hdr["value"]

		return info

	def get_message_by_id(self, mid, uid="me"):
		message = self._service.users().messages().get(userId=uid, id=mid, format="raw").execute()

		msg_bytes = base64.urlsafe_b64decode(message["raw"].encode("ASCII"))

		msg_mime = email.message_from_bytes(msg_bytes)
		return msg_mime

	def save_message_by_id(self, mid, uid="me", filename=None):
		if filename is None:
			filename = mid + ".eml"

		message = self._service.users().messages().get(userId=uid, id=mid, format="raw").execute()

		msg_bytes = base64.urlsafe_b64decode(message["raw"].encode("ASCII"))
		with open(filename, "wb") as f:
			f.write(msg_bytes)
	
	def save_attachments_by_id(self, mid, uid="me", savedir="."):
		message = self._service.users().messages().get(userId=uid, id=mid).execute()

		for part in message["payload"]["parts"]:
			if part["filename"] and len(part["filename"]) > 0:
				if "data" in part["body"]:
					data=part["body"]["data"]
				else:
					aid=part["body"]["attachmentId"]
					att=self._service.users().messages().attachments().get(userId=uid, messageId=mid,id=aid).execute()
					data=att["data"]
				data = base64.urlsafe_b64decode(data.encode("UTF-8"))
				if not os.path.exists(savedir):
					os.makedirs(savedir)
				with open(os.path.join(savedir, part["filename"]), "wb") as f:
					f.write(data)

