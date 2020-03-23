import argparse
import os
import yagmail

import constants


class EMailSending:

    def __init__(self):
        self.__fromuser = constants.SENT_FROM_USER
        self.__frompassword = constants.SENT_FROM_PASSWORD


    def sendEMail(self, to_users: list, attached_files_paths: list):
        '''
        Send files as an e-mail to recipients
        :param to_users: recipients of e-mail
        :param attached_files_paths: files for sending
        '''
        # Connect to SMTP server
        smtp_connection = yagmail.SMTP(user=self.__fromuser, password=self.__frompassword,
                                       host='smtp.gmail.com')
        email_subject = 'SportAISystem 1.0 Statistics'
        # Send the email
        smtp_connection.send(to_users, email_subject, attached_files_paths)


def init_argparse():
    '''
    Initializes argparse
    '''
    parser = argparse.ArgumentParser(description='Sending statistics by the use of e-mail')
    parser.add_argument(
        '--to',
        nargs='?',
        help='E-mail of recipient',
        required=True,
        type=str)
    parser.add_argument(
        '--folder',
        nargs='?',
        help='Folder with files to send',
        required=True,
        type=str)
    return parser


def main():
    parser = init_argparse()
    # Extract arguments of script
    args = parser.parse_args()
    sending = EMailSending()
    # Collect sending files
    content = [os.path.join(os.path.abspath(args.folder), file) for file in os.listdir(args.folder)]
    sending.sendEMail([args.to], content)


if __name__ =='__main__':
    main()