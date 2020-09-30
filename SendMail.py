"""@Aditya Singh Tejas (c) 2020 PIERA-ZONE"""
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

def Send_response(res_email): #Send mail of the response to the teacher
    with open(os.path.join(root_dir, "Student_Input.txt"),'r') as file:
        filename = str(file.read())
        name = filename.split('_')[1]
        file.close()       
    subject = "Submission Received | PIERA-ZONE"
    body = ("The following submission has been received from "+name+".\n"
            +"Please find the attatched file containing the responses.\n\n"
            +"Cheers\n© 2020 PIERA-ZONE")            
    sender_email = "piera_zone@yahoo.com"
    receiver_email = res_email 
    password = "dvgayjfvlajmpviu"
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    with open("Student Responses//"+filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())        
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
    message.attach(part)
    text = message.as_string()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)
    return 0

def Send_results(res_email, filename, name): #Send student results to the students post evaluation    
    subject = "Results Out | PIERA-ZONE"

    body = (f"Results for the {name} (exam) has been declared.\n"
            +"Please find the attatched file containing your result.\n\n"
            +"Cheers\n© 2020 PIERA-ZONE")           
    sender_email = "piera_zone@yahoo.com"
    receiver_email = res_email 
    password = "dvgayjfvlajmpviu"
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    with open(filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())        
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {os.path.basename(filename)}",
    )
    message.attach(part)
    text = message.as_string()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)
    return 0

global root_dir
root_dir = os.path.join('Program Files', 'Cache')






   
