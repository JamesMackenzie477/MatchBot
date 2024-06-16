import random
from threading import Lock, Timer
from Utils import ExList

# Only have one instance of a proxy in the manager.
# Return just the proxy address from random_proxy.
# Use the proxy address in otehr functions, not proxy objects.

# A proxy object used within the proxy manager.
class Proxy:

	# Creates a new proxy instance.
	def __init__(self, proxy):
		# Sets the proxy address.
		self.proxy = proxy
		# Unlocks the proxy.
		self.locked = False

	# Defines the string method for casting.
	def __str__(self):
		# Returns the proxy address.
		return self.proxy

	# Defines the is equal method for comparison operations.
	def __eq__(self, other):
		# Compares the proxy address and lock.
		if self.proxy == other.proxy and self.locked == other.locked:
			# Objects are equal.
			return True
		else:
			# Objects are not equal.
			return False


# A proxy manager used to manage proxies over a multithreaded program.
class ProxyManager:

	# Creates a new proxy factory with a given list of proxies.
	def __init__(self, proxies):
		# Converts the proxies to proxy objects.
		self.__proxies = ExList(Proxy(proxy) for proxy in proxies)
		# A lock used to make the class thread safe.
		self.lock = Lock()

	# Returns a random proxy from the internel proxy list.
	def random_proxy(self):
		# Loops until an unlocked proxy is found.
		while True:
			# Uses a lock to get a proxy.
			with self.lock:
				# Gets a random proxy.
				proxy = random.choice(self.__proxies)
				# Checks if the proxy is locked
				if not proxy.locked:
					# Duplicates the proxy since a referance is needed.
					locked_proxy = Proxy(proxy.proxy)
					# Locks the duplicated proxy.
					locked_proxy.locked = True
					# Locks the original proxy by replacing it with the locked proxy.
					self.__proxies.replace(proxy, locked_proxy)
					# Returns the locked proxy.
					return locked_proxy

	# Locks the given proxy until the set interval has elapsed.
	def proxy_cooldown(self, proxy, seconds):
		# Locks the proxy.
		self.lock_proxy(proxy)
		# Creates a new timer used to call the callback function.
		timer = Timer(interval=seconds, function=self.unlock_proxy, args=[proxy])
		# Starts the timer.
		timer.start()

	# Locks the given proxy.
	def lock_proxy(self, proxy):
		# Duplicates the proxy since a referance is needed.
		locked_proxy = Proxy(proxy.proxy)
		# Locks the duplicated proxy.
		locked_proxy.locked = True
		# Uses a lock to replace an element.
		with self.lock:
			# Locks the original proxy by replacing it with the locked proxy.
			self.__proxies.replace(proxy, locked_proxy)
		# Returns the locked proxy.
		# return locked_proxy

	# Unlocks the given proxy.
	def unlock_proxy(self, proxy):
		# Duplicates the proxy since a referance is needed.
		unlocked_proxy = Proxy(proxy.proxy)
		# Uses a lock to replace an element.
		with self.lock:
			# Unlocks the original proxy by replacing it with the unlocked proxy.
			self.__proxies.replace(proxy, unlocked_proxy)
		# Returns the unlocked proxy.
		# return unlocked_proxy

	# Removes the given proxy from the manager.
	def remove_proxy(self, proxy):
		pass