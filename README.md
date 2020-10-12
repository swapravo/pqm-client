# Post Quantum Mail

## [PostQuantumMail](https://www.postquantummail.com) aims to revolutionise the way we mail.

Currently, it uses [CodeCrypt](https://github.com/exaexa/codecrypt) as its quatum safe cryptographic backend and we plan to port it to [LibOQS](https://github.com/open-quantum-safe/liboqs) when it comes of age.

### Core ideas and Features:

* End-to-End encrypted mails (**including** subjects and attachments)
  * With quantum-safe encryption algorithms and signature schemes.
  * All we (and anyone who eventually breaks into our systems) can ever see
	is the sender's and reciepient's address.

* No Advertisements.

* Free for personal use with access to all features.
	Upgrade only for "out-of-the-box" or corporate use cases.

* Private keys are generated on your device and **never** leave it.

* It tries to **remove all points of trust** from the mail service provider itself (here, us).
	Just because you use our services does **not** mean you have to trust us.

* Considering a situation, where a mail service provider has been compromised in such 
	a way that the signup/login scripts send a copy of credentials to the attackers,
	it might prove to be long, before someone actually discovers this. PQm plans to be
	accesssible only thorough its open source client.

* **Both** GUI and CLI interfaces!

* Your mails do not become 1.4x their original size, as is the case with others. So, you can store 1.4x more mails with the same storage capacity with us.


TODO List
1. bash-like interface for managing mailboxes. (As in cd /inbox. or rm flipkart*)
2. GUI
3. A log pane that list all the background activities.
4. Folders in one's mailbox.
5. Pagination of info.
6. create a seperate user for this app. let it own all rights to its files.
