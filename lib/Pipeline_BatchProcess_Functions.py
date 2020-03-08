import smtplib
from email.mime.text import MIMEText
from email.header import Header

def send_alerting_email(error_msg):
    
    smtpserver = 'smtp.163.com'
    user = 'NEC_lab@163.com'
    with open(r'D:\ZOE-STORE-LAPTOP\NEC_lab_163_credential.txt', 'r') as file:
        credential = file.read().replace('\n', '')

    sender = 'NEC_lab@163.com'
    receiver = 'zoehcycy@gmail.com'
    subject = 'Unhandled Exception'

    msg = MIMEText('Exception:\n' + e,'plain','utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = 'NEC_lab<NEC_lab@163.com>'  
    msg['To'] = "zoehcycy@gmail.com"

    smtp = smtplib.SMTP()
    smtp.connect(smtpserver)
    smtp.login(user, credential)
    smtp.sendmail(sender, receiver, msg.as_string())
    smtp.quit()
    
    print()