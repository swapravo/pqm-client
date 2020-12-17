import src.globals

def help():

    """
    Welcome to PostQuantumMail!

    This quickstart module will help you personalise the app and manage your mailbox.


    M  A  I  L  B  O  X

    Your Mailbox has been divided into directories "/dir" for easy management.
    You can traverse directories with cd. You can create new directories too.

    inbox   -> /inbox
    sent    -> /sent
    drafts  -> /drafts
    starred -> /imp
    archive -> /archive
    spam    -> /spam
    trash   -> /bin


    Commands:


    connect             : Connect to the server when this app starts (ON by default)
    disconnect          : Disconnect from the server / Stop trying to reconnect
                            to the server

    ls                  : list recent mails
    ls N                : list N recent mails from current /dir
    ls /dir             : list recent mails from /dir
    ls N /dir           : list the last N mails in directory /dir.
    ls sender@address.com : list all mails sent from/to sender@address.com
                          *Default value for (recent=N) is 10.

    open (OR <enter>)       : Open current mail
    open N                  : open mail N
    close (OR <alt> + <- )  : Close the current mail \
                                Switch the directory view
    next (OR ->)            : Display the next mail
    previous (OR <-)        : Display the previous mail
    next N (OR <space>)     : Display the next N mails as a list

    write                         : Start writing a mail
    writeto recipient@address.com : Start writing a mail and send it to recipient(s).

    cd                  : cd /inbox
    cd /dir             : change directory to /dir

    sync                : Fetch new mails.

    send                : Send any mails still lurking in the outbox

    rm                  : Remove the current mail
    rm N                : Remove mail N
    rm sender1          : Remove mails sent by sender sender1
    rm (from/to) sender@spam.com  : Remove mails from/to sender@spam.com

    grep                : Grep your mails!

    awk                 : Awk your mails!

    spammer sender@spam.com : Add sender@spam to spammer's list.
    block sender@spam.com   : Block emails from sender@spam.com


    S  E  T  T  I  N  G  S

    addkey user@postquantummail.com : Add user `user`s public keys
                                      This will be done automatically when sending
                                      a mail to someone.

    rmkey user@postquantummail.com : Remove user `user`s public keys

    lskey user@postquantummail.com : Displays the:
                                            i) The Key
                                            ii) Blake 2b Hash of the Key
                                            iii) An unique graphical representation
                                                    of this key.

    lskey all : Display all keys in the keyring

    settings            : Change user preferences



    Read the full guide at www.postquantummail.com/doc

    """


    print(help.__doc__)


def edit_config():
    pass


def shell():
    pass
