import smtplib
import imghdr
from email.message import EmailMessage
import glob
import os


def clean_folder():
    images = glob.glob("images/*.png")
    for image in images:
        os.remove(image)


PASSWORD = os.getenv("PASSWORD")
SENDER = "ishikasethi2806@gmail.com"


def send_email(object_image, receiver):
    message = EmailMessage()
    message['Subject'] = "Motion Detected!"
    text = f"""Hello {receiver},
Thank you for taking your time to use the app. The below attachment is the image of the object caught as a motion!"""
    message.set_content(text)

    with open(object_image, 'rb') as file:
        content = file.read()
    message.add_attachment(content, maintype="image", subtype=imghdr.what(None, content))

    gmail = smtplib.SMTP("smtp.gmail.com", 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(SENDER, PASSWORD)
    gmail.sendmail(SENDER, receiver, message.as_string())
    gmail.quit()


if __name__ == "__main__":
    send_email(object_image="test_images/test.png")
