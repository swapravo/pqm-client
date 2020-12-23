from sys import exit	# PYL-W0622

import src.globals
import src.requests
import src.shell
import src.utils


src.globals.TEMP_FOLDER = src.utils.mount_temp_directory()

def main():
	print("\nPost Quantum Mail:\n")

	while True:
		try:
			choice = 2 #int(input("1. Login\t2. Signup\t3. Username avail check\t4. Exit: "))
		except ValueError:
			continue

		if choice > 5 or choice < 1:
			continue
		if choice == 1:
			src.requests.login()
		elif choice == 2:
			src.requests.signup()
			break # DEVEL FEATURE
		elif choice == 3:
			src.requests.username_availability_check()
			break # DEVEL FEATURE
		elif choice == 4:
			print("\nExiting...\n")
			exit()
		else:
			src.shell.help()
			continue
