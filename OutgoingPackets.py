#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id$

import types
import sys
import struct
from HeaderPacket import GGHeader
from Networking import Connection
import Helpers
from Helpers import Enum

GGOutgoingPackets = Enum({
	"GGNewStatus":0x0002, #Zmiana statusu
	"GGPing":0x0008, #Ping
	"GGSendMsg":0x000b, #Wyslanie wiadomosci
	"GGLogin":0x000c, #Logowanie sie przed GG 6.0
	"GGAddNotify":0x000d, #Dodanie do listy kontaktow
	"GGRemoveNotify":0x000e, #Usuniecie z listy kontaktow
	"GGNotifyFirst":0x000f, #Poczatkowy fragment listy kontaktow wiekszej niz 400 wpisow
	"GGNotifyLast":0x00010, #Ostatni fragment listy kontaktow
	"GGLoginExt":0x0013, #Logowanie przed GG 6.0
	"GGPubDir50Request":0x0014, #Zapytanie katalogu publicznego
	"GGLogin60":0x0015, #Logowanie
	"GGUserlistRequest":0x0016, #Zapytanie listy kontaktow na serwerze
	"GGLogin70":0x0019 #Logowanie
	})

class GGOutgoingPacket(object):
	"""
	"Abstrakcyjna" klasa pakietow wysylanych do serwera
	"""
	def send(self):
		pass


class GGLogin(GGOutgoingPacket):
	"""
	Pakiet ten wysylamy do serwera, zeby sie zalogowac
	"""
	def __init__(self, uin, password, status, seed, description = "", local_ip = "127.0.0.1", local_port = 1550, \
				external_ip = "127.0.0.1", external_port = 0, image_size = 255, time = 0):
		"""
		uin - numer gadu-gadu (int)
		password - haslo (string)
		status - status poczatkowy (GGStatus)
		seed - seed z pakietu GGWelcome (int)
		"""
		assert type(uin) == types.IntType
		assert type(password) == types.StringType
		#assert type(status) in GGStatus
		#assert type(seed) == types.IntType or type(seed) == types.LongType
		assert type(description) == types.StringType and len(description) <= 70
		assert type(local_ip) == types.StringType
		assert type(local_port) == types.IntType
		assert type(external_ip) == types.StringType
		assert type(external_port) == types.IntType
		assert type(time) == types.IntType
		assert type(image_size) == types.IntType
		
		self.uin = uin
		self.password = password
		self.status = status
		self.seed = seed
		self.local_ip = local_ip
		self.local_port = local_port
		self.description = description
		self.external_ip = external_ip
		self.external_port = external_port
		self.image_size = image_size
		self.time = time
		self.version = 0x27 # GG 7.0

	def send(self, connection):
		assert type(connection) == Connection
		
		"""
		#data = struct.pack("<IBIIIBIHIHBB%dsI" % (len(self.description) + 1),
		data = struct.pack("<IB64sIIBIHIHBB%dsI" % (len(self.description) + 1),
			self.uin, 
			0x01, 
			Helpers.gg_login_hash(self.password, self.seed), 
			self.status, 
			self.version, 
			0x00, 
			Helpers.ip_to_int32(self.local_ip), 
			self.local_port, 
			Helpers.ip_to_int32(self.external_ip), 
			self.external_port, 
			self.image_size, 
			0xbe,
			self.description,
			self.time)

		#connection.send(repr(GGHeader(GGOutgoingPackets.GGLogin, len(data))) + data)
		"""
		data = struct.pack("<IIIIBIhIhBB%dsI" % (len(self.description) + 1),
			self.uin, Helpers.gg_login_hash(self.password, self.seed), self.status, self.version, 0x00,
			Helpers.ip_to_int32(self.local_ip), self.local_port, Helpers.ip_to_int32(self.external_ip), self.external_port,
			self.image_size, 0xbe, self.description, self.time)

		connection.send(repr(GGHeader(GGOutgoingPackets.GGLogin60, len(data))) + data)

class GGNewStatus(GGOutgoingPacket):
	"""
	Pakiet ten wysylamy do serwera, zeby zmienic status
	"""
	def __init__(self, status, description = '', time = 0):
		"""
		status - status (GGStatus)
		description - opis statusu (string)
		time - czas w sekundach od 1.01.1970
		"""
		assert type(status) == types.IntType
		assert type(description) == types.StringType and len(description) <= 70
		assert type(time) == types.IntType or type(time) == types.LongTime
		
		self.status = status
		self.description = description
		self.time = time

	def send(self, connection):
		assert type(connection) == Connection
		
		data = struct.pack("<I%dsI" % (len(self.description) + 1), self.status, self.description, self.time)
		connection.send(repr(GGHeader(GGOutgoingPackets.GGNewStatus, len(data))) + data)
		
class GGSendMsg(GGOutgoingPacket):
	"""
	Pakiet wysylamy do serwera, zeby wyslac wiadomosc
	"""
	def __init__(self, rcpt, msg, seq = 0, msg_class = 0x0004):
		"""
		rcpt - numer odbiorcy
		seq - numer serwencyjny wiadomosci
		msg_class - klasa wiadomosci
		msg - wiadomosc
		"""
		assert type(rcpt) == types.IntType and rcpt > 0
		assert type(seq) == types.IntType and seq > 0
		assert type(msg_class) == types.IntType
		assert type(msg) == types.StringType and len(msg) <= 2000
		
		self.rcpt = rcpt
		self.seq = seq
		self.msg_class = msg_class
		self.msg = msg
		
	def send(self, connection):
		assert type(connection) == Connection
		
		data = struct.pack("<III%ds" % (len(self.msg) + 1), self.rcpt, self.seq, self.msg_class, self.msg)
		connection.send(repr(GGHeader(GGOutgoingPackets.GGSendMsg, len(data))) + data)
		
