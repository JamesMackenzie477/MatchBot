from threading import Lock
import sys
# A collection of thread safe functions to be used with multithreading

# A lock used for printing.
print_lock = Lock()

# A thread safe version of print that uses a lock.
def thread_print(*objects, sep=' ', end='\n', file=sys.stdout, flush=False):
	# Uses the print lock.
	with print_lock:
		# Prints the arguments.
		print(*objects, sep=sep, end=end, file=file, flush=flush)

# A class to interact with a file over threads.
class ThreadFile:

	# Creates a new thread file.
	def __init__(self, file):
		# Sets the output file name
		self.file = file
		# Creates a lock.
		self.lock = Lock()

	# Clears the file.
	def clear(self):
		# Uses the file lock.
		with self.lock:
			# Clears the output file.
			with open(self.file, 'w') as f:
				# Closes the output file.
				pass

	# Appends to the file.
	def append(self, string):
		# Uses the file lock.
		with self.lock:
			# Opens the file.
			with open(self.file, 'a') as f:
				# Writes the string to the file.
				f.write(string)