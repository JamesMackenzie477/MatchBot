import requests

# A wrapper for the ipstack API.
class IPStack:

	# Creates a new instance of the ipstack API.
	def __init__(self, access_key):
		# Sets the access key.
		self.access_key = access_key

	# Returns the details of the given IP address in a json format.
	def lookup(self, ip_address):
		# Creates the request params.
		params = {'access_key': self.access_key}
		# Looks up the IP address and returns the data.
		return requests.get('http://api.ipstack.com/{}'.format(ip_address), params=params).json()