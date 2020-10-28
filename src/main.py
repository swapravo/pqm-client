from sys import exit	# PYL-W0622


import src.login
import src.signup
import src.shell

def main():
	print("\nPost Quantum Mail:\n")

	while True:
		try:
			# TF IS WRONG WITH \t4. HELP???
			choice = int(input("1. Login\t2. Signup\t3. Exit: "))
		except ValueError:
			continue

		if choice > 4 or choice < 1:
			continue
		if choice == 1:
			src.login.login()
		elif choice == 2:
			src.signup.signup()
		elif choice == 3:
			print("\nExiting...\n")
			exit()
		else:
			src.shell.help()
			continue
