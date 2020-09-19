from sys import exit


import src.frontend


def main():
	print("\nPost Quantum Mail:\n")

	while True:
		try:
			choice = int(input("1. Login\t2. Signup\t3.Exit : "))
		except ValueError:
			continue

		if choice > 3 or choice < 1:
			continue
		if choice == 1:
			src.frontend.login()
		elif choice == 2:
			src.frontend.signup()
		else:
			print("\nExiting...\n")
			exit()
