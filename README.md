# Post Quantum Mail

## [PostQuantumMail](https://www.postquantummail.com) aims to revolutionise the way we mail.

### Core ideas and Features:

* End-to-End encrypted mails (**including** subjects and attachments)
  * With quantum-safe encryption algorithms and signature schemes.
  * All we can ever see	is the sender's and reciepient's address.

* Sick of advertisements? We are too. So, no advertisements for you!

* No foreceful collection of personal information:
  * No phone numbers, *unless you want* to opt for 2FA.
  * No linking you to other addresses, disguised in the form of "recovery mail addresses", *unless you want it.*

* Free for personal use.
  * Upgrade only for "out-of-the-box" or corporate use cases.

* Your keys are generated on your device and the secret keys **never** leave it.

* Verifiable trust policy: Just because you use our services does **not** mean you have to trust us.
	* Cryptographically-signed mails.
	* Open source applications for you to tinker with.

* Most people use webmail clients to login / signup. In case a compromised / malicious mail service provider takes a copy of the credentials,
	it might prove to be long, before someone actually discovers this. PQm plans to be accesssible through the browser or the terminal using its **open source client**.

* **Both** GUI and CLI interfaces!

* Store 1.4x more mails with the same storage capacity with us.[*](http://www.postquantummail.com/faq/#1.4). 
Your mails do not become 1.4x their original size, as is the case with others.

### Technicals

We advise you to, and would really appreciate it, if you check out the technicals.

* Currently, we use [CodeCrypt](https://github.com/exaexa/codecrypt) as the quantum-safe cryptographic backend and we plan to port it to [LibOQS](https://github.com/open-quantum-safe/liboqs) when it comes of age.

* [Whitepaper](https://wwww.postquantummail.com/technical/technical-whitepaper-latest.pdf)
