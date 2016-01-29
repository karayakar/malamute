from __future__ import print_function, absolute_import
import czmq
from ._malamute_ctypes import MlmClient

try:
	range = xrange
except NameError:
	pass

class MalamuteError(Exception):
	pass

def _list_to_zmsg(parts):
	assert isinstance(parts, (list, tuple))
	zmsg = czmq.Zmsg()
	for p in parts:
		zmsg.addstr(p)
	return zmsg

def _zmsg_to_list(zmsg):
	size = zmsg.size()
	return [zmsg.pop().strdup() for _ in range(size)]

class MalamuteClient(object):
	"""
	A pythonic wrapper for the generated MlmClient.
	"""
	def __init__(self):
		self.c = MlmClient()

	def _check_error(self, return_value, fmt, *args, **kw):
		if return_value != 0:
			raise MalamuteError(fmt.format(*args, **kw) + ': ' + self.c.reason())

	def connected(self):
		return self.c.connected()

	def connect(self, endpoint, timeout, address):
		self._check_error(
			self.c.connect(endpoint, timeout, address),
			"Could not connect to malamute server at {!r}", endpoint,
		)

	def set_producer(self, stream):
		self._check_error(
			self.c.set_producer(stream),
			"Could not set producer",
		)

	def set_worker(self, address, pattern):
		self._check_error(
			self.c.set_worker(address, pattern),
			"Could not set worker",
		)

	def set_consumer(self, stream, pattern):
		self._check_error(
			self.c.set_consumer(stream, pattern),
			"Could not set consumer",
		)

	def send(self, subject, content):
		self._check_error(
			self.c.send(subject, _list_to_zmsg(content)),
			"(send) Could not send stream message",
		)

	def sendto(self, address, subject, tracker, timeout, content):
		self._check_error(
			self.c.sendto(address, subject, tracker, timeout, _list_to_zmsg(content)),
			"(sendto) Could not send direct message",
		)

	def sendfor(self, address, subject, tracker=None, timeout=0, content=''):
		self._check_error(
			self.c.sendfor(address, subject, tracker, timeout, _list_to_zmsg(content)),
			"(sendfor) Could not send service message",
		)

	def recv(self):
		m = self.c.recv()
		return self.c.command(), self.c.sender(), self.c.subject(), _zmsg_to_list(m)
