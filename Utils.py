# A few useful Python functions.

# Adds a few extra useful functions to the Python standard list.
class ExList(list):

	# Replaces an element in the list with another element.
	def replace(self, target, source):
		# Iterates thtough the lists elements.
		for index, element in enumerate(self):
			# Compares the element to the target element.
			if element == target:
				# Replaces the element.
				self[index] = source