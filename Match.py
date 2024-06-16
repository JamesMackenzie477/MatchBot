import requests
import base64
from Crypto.Cipher import AES
from Crypto import Random

# Pads a string for encryption.
pad = lambda s: s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size) 


# Used for Match API errors.
class MatchException(Exception):

	# Creates a new instance of the Match exception class.
	def __init__(self, message, err_code):
		# Call the base excepetion class.
		super(MatchException, self).__init__(message)
		# Sets the error code.
		self.err_code = err_code


# Wrapper for a Match API response.
class MatchResponse:

	# Creates a new instance of the Match response class.
	def __init__(self, response):
		# Sets the response attribute.
		self.response = response

	# Raises an exception if there is a problem with the API.
	def check_status(self):
		#try:
		# Raises an exception if the status is an error.
		self.response.raise_for_status()
		#except requests.exceptions.HTTPError:
		# Constructs the error message.
		#err_msg = 'Bad status code: {}'.format(self.response.status_code)
		# Raises a bad status code exception.
		#raise MatchException(err_msg, None)

	# Checks if the response is an error.
	def check_for_error(self):
		# Casts the response data to json format.
		res_data = self.response.json()
		# Attemps to get an error.
		try:
			# Gets the error value.
			err = res_data['Error']
			# Checks if there is an error value.
			if err:
				# Gets the error message
				err_msg = err['Message']
				# Gets the error code.
				err_code = err['Number']
				# Raises a Match error.
				raise MatchException(err_msg, err_code)
		# If there is no error.
		except KeyError:
			# Ignore the error.
			pass

	# Returns the response data in json format.
	def get_data(self, **kwargs):
		# Returns the response data in json format.
		return self.response.json(**kwargs)

	# Returns the status code of the response.
	def get_status(self):
		# Returns the status code.
		return self.response.status_code


# An account session for the Match API.
class MatchAccount:

	# Creates a new instance of the Match account class.
	def __init__(self, age, gender, postal, country, birthday, subscribed):
		# Sets the account session attributes.
		# self.__auth = auth
		self.age = age
		self.gender = gender
		self.postal = postal
		self.country = country
		self.birthday = birthday
		self.subscribed = subscribed

	# The class string method.
	def __str__(self):
		# Returns a string of the class attributes.
		return "Age: {}\nGender: {}\nZipcode: {}\nContry: {}\nBirthday: {}\nSubscription Plan: {}".format(self.age, self.gender, self.postal, self.country, self.birthday, self.subscribed)

	# The class representation method.
	def __repr__(self):
		# Returns the result of the __str__ method.
		return self.__str__()


# A wrapper for the Match mobile API.
class Match:

	# Stores the match API domain address.
	API_DOMAIN = 'g3.match.com'
	# Stores the session directory.
	SES_DIR = '/rest/session/sitecode=1'
	# Stores the login directory.
	LOGIN_DIR = '/rest/login/sitecode=1/logpagecode=false/isautologin=false'
	# Stores the mobile app user agent.
	USER_AGENT = 'match.com/18.05.06 Android/6.0.1 (Innotek GmbH VirtualBox; resolution 768x976)'
	# Stores the API auth key.
	AUTH_KEY = ',MatchFD51DE89D449,13,6'
	# Stores the API secondary auth key start.
	SEC_AUTH = 'MatchFD51DE89D449_6'
	# Stores the mobile id of the device.
	MOBILE_ID = '79f2e26a317a7ab6'
	# Stores the app version
	APP_VER = '18.05.06'
	# Stores the device os version.
	OS_VER = '6.0.1'
	# Stores the device banner id.
	BANNER_ID = '671501'
	# Stores the device tracking id.
	TRACK_ID = '525952'

	# Creates a new instance of the Match API.
	def __init__(self):
		# Creates a session.
		self.session = requests.session()
		# Gets a session token.
		self.token = self.get_session_token()

	# Asks the server to create a new session token.
	def get_session_token(self):
		# Constructs the request auth headers
		auth_head = {'Authorization': Match.AUTH_KEY, 'User-Agent': Match.USER_AGENT}
		# Constructs the session data.
		ses_data = {'mobileid': '79f2e26a317a7ab6', 'appVersion': '18.05.06', 'deviceos': '6.0.1', 'bannerId': '671501', 'trackingId': '525952'}
		# Posts the login request to the API.
		res = MatchResponse(self.session.post('https://g3.match.com/rest/session/sitecode=1', headers=auth_head, data=ses_data))
		# Raise an exception if there is a status error.
		res.check_status()
		# Raise an exception if there is an error.
		res.check_for_error()
		# Gets the response data.
		res_data = res.get_data()
		# Returns the session token.
		return res_data['Payload']['Token']

	# Constructs an auth key via the session token.
	def __get_auth_key(self):
		# Constructs and returns a new auth key.
		return '{}{}'.format(self.token, Match.AUTH_KEY)

	# Constructs a secondary auth key.
	# This key encrypts the email and password of the logging in user.
	# It does this to stop crackers by ensuring that the auth key when decrypted matches the email and password.
	# This is the reason this program is worth so much.
	def __get_secondary_auth_key(self, email, password):
		# Creates the string to encrypt.
		enc_str = '{}:{}'.format(email, password)
		# Generates an AES encryption key.
		key = Random.new().read(AES.block_size)
		# Gets the bytes of the encryptable string.
		enc_str_bytes = pad(enc_str).encode('utf-8')
		# Decodes the session token.
		tok_dec = base64.b64decode(self.token)
		# Caps the token size.
		tok_dec = tok_dec[:min(len(tok_dec), 32)]
		# Creates a new AES cypher block chain encryption
		cipher = AES.new(tok_dec, AES.MODE_CBC, key)
		# Encrypts the encryptable string.
		enc = cipher.encrypt(enc_str_bytes)
		# Constructs the auth token.
		auth = '{}{}'.format('1:', base64.b64encode(enc + key).decode('iso-8859-1'))
		# Returns the full auth token.
		return '{} {}'.format(Match.SEC_AUTH, base64.b64encode(auth.encode('utf-8')).decode('iso-8859-1'))

	# Creates a login session with the specified Match account.
	def login(self, email, password):
		# Constructs the request auth headers
		auth_head = {'Secondary-Authorization': self.__get_secondary_auth_key(email, password), 'Authorization': self.__get_auth_key(), 'User-Agent': Match.USER_AGENT}
		# Constructs the login data.
		log_data = {'password': password, 'clientappversion': '18.05.06', 'clientos': '6.0.1', 'handle': email, 'bannerId': '671501', 'trackingid': '525952'}
		# Posts the login request to the API.
		res = MatchResponse(self.session.post('https://g3.match.com/rest/login/sitecode=1/logpagecode=false/isautologin=false', headers=auth_head, data=log_data))
		# Raise an exception if there is a status error.
		res.check_status()
		# Raise an exception if there is an error.
		res.check_for_error()
		# Gets the response data.
		res_data = res.get_data()
		# Gets the response payload.
		payload = res_data['Payload']
		# Gets the user's birthday.
		birthday = self.get_profile(payload['AuthToken'], payload['UserId'])['birthDay']
		# Creates and returns a new match account object with the returned details.
		return MatchAccount(payload['Age'], payload['Gender'], payload['Postal'], payload['Country'], payload['Birthday'], payload['IsSubscribed'])

	# Returns the profile of the given user id.
	def get_profile(self, auth, user_id):
		# Constructs the request auth headers
		auth_head = {'Authorization': '{}{}'.format(auth, Match.AUTH_KEY), 'User-Agent': Match.USER_AGENT}
		# Constructs the profile params.
		prof_params = {'dontLogView': 'true'}
		# Posts the login request to the API.
		res = MatchResponse(self.session.get('https://g3.match.com/api/android/user/{}/profile'.format(user_id), headers=auth_head, params=prof_params))
		# Raise an exception if there is a status error.
		res.check_status()
		# Raise an exception if there is an error.
		res.check_for_error()
		# Gets the response data.
		res_data = res.get_data()
		# Gets and returns the response payload.
		return res_data['payload'][0]


# Allows the use of a proxy with the Match mobile API.
class MatchProxy(Match):

	# Creates a new instance of the Match API.
	def __init__(self, proxy):
		# Creates a session.
		self.session = requests.session()
		# Sets the session proxy.
		self.session.proxies.update({'http': proxy, 'https': proxy})
		# Does not verify the SSL certificate of the proxy.
		self.session.verify = False
		# Gets a session token.
		self.token = self.get_session_token()


if __name__ == '__main__':
	# Creates a new instanace of the match API.
	match = Match()
	# Logs into the given account.
	account = match.login('fuc.king@outlook.com', 'fuckschool123')
	# Prints the account object.
	print(account)
	# Waits for the user.
	input()