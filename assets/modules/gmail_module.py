import keyboard 
import smtplib 
from threading import Timer

import imaplib
import email
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from email.mime.application import MIMEApplication


# Email information
class Email:
    def __init__(self, email, password):
        self.email = email
        self.password = password



    def sendmail(self, emailreceiver, subject, body,path_to_pdf_file,path_to_excel_file):
        # Email configuration
        email = self.email
        sender_password = self.password
        recipient_email = emailreceiver
        

        # File path to the PDF you want to attach
        pdf_attachment_path = path_to_pdf_file  
        excel_attachment_path = path_to_excel_file

        # Create the MIME object
        message = MIMEMultipart()
        message["From"] = email
        message["To"] = recipient_email
        message["Subject"] = subject

        
        message.attach(MIMEText(body, "plain"))

        # Attach the PDF file
        if pdf_attachment_path:
            with open(pdf_attachment_path, "rb") as pdf_file:
                pdf_attachment = MIMEApplication(pdf_file.read(), _subtype="pdf")
                pdf_attachment.add_header("Content-Disposition", f"attachment; filename={pdf_attachment_path}")
                message.attach(pdf_attachment)

        if excel_attachment_path:
            with open(excel_attachment_path, "rb") as excel_file:
                excel_attachment = MIMEApplication(excel_file.read(), _subtype="xlsx")
                excel_attachment.add_header("Content-Disposition", f"attachment; filename={excel_attachment_path}")
                message.attach(excel_attachment)
        # Connect to the SMTP server (in this case, Gmail's SMTP server)
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            # Start TLS for security
            server.starttls()

            # Login to the email account
            server.login(email, sender_password)

            # Convert the message to a string and send it
            server.sendmail(email, recipient_email, message.as_string())

        print("Email with attachment sent successfully!")

    # Call the function to send the email with the attachment




    

    def receiveemail(self, emailsender, emailsubject, GetNewest=True):
        try:
            # Connect to the IMAP server (Gmail in this case)
            imap = imaplib.IMAP4_SSL("imap.gmail.com")
            imap.login(self.email, self.password)
            imap.select("inbox")

            # Search for emails from a specific sender with a specific subject
            sender = emailsender
            subject = emailsubject

            # Construct the search query
            search_query = f'(FROM "{sender}" SUBJECT "{subject}")'

            # Search for emails that match the query
            result, data = imap.search(None, search_query)

            # Get the list of email IDs that match the search criteria
            email_ids = data[0].split()

            if not email_ids:

                return None

            if GetNewest:
                # Get the ID of the newest email (last in the list)
                newest_email_id = email_ids[-1]

                # Fetch the email by its ID
                result, message_data = imap.fetch(newest_email_id, "(RFC822)")

                # Parse and return the message content of the newest email
                raw_email = message_data[0][1]
                email_message = email.message_from_bytes(raw_email)

                # Get the message content
                message_content = ""
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        message_content = part.get_payload(decode=True).decode("utf-8")
                        break  # Stop when the plain text part is found

                # Logout and close the connection
                imap.logout()

                return message_content  # Return the message content
            else:
                # Iterate through email IDs and fetch each email
                emails = []

                for email_id in email_ids:
                    # Fetch the email by its ID
                    result, message_data = imap.fetch(email_id, "(RFC822)")

                    # Parse the email
                    raw_email = message_data[0][1]
                    email_message = email.message_from_bytes(raw_email)

                    # Get the message content
                    message_content = ""
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            message_content = part.get_payload(decode=True).decode("utf-8")
                            break  # Stop when the plain text part is found

                    emails.append(message_content)  # Append message content to the list

                # Logout and close the connection
                imap.logout()

                return emails  # Return a list of message contents
        except Exception as e:
            print(f"An error occurred: {str(e)}")


            
    def delete_email(self, emailsender, emailsubject):
        try:
            # Connect to the IMAP server (Gmail in this case)
            imap = imaplib.IMAP4_SSL("imap.gmail.com")
            imap.login(self.email, self.password)
            imap.select("inbox")

            # Search for emails from a specific sender with a specific subject
            sender = emailsender
            subject = emailsubject

            # Construct the search query
            search_query = f'(FROM "{sender}" SUBJECT "{subject}")'

            # Search for emails that match the query
            result, data = imap.search(None, search_query)

            # Get the list of email IDs that match the search criteria
            email_ids = data[0].split()

            if not email_ids:
                
                return

            # Iterate through email IDs and delete each email
            for email_id in email_ids:
                imap.store(email_id, '+FLAGS', '(\Deleted)')

            # Expunge to permanently delete the marked emails
            imap.expunge()

            

            # Logout and close the connection
            imap.logout()

        except Exception as e:
            print(f"An error occurred: {str(e)}")
