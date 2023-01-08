import streamlit as st
import re
import cv2
import time
from functions import *
from threading import Thread

st.set_page_config(layout='wide')

st.title("Webcam Motion Detector Web App")
st.write("This app records the initial state of the camera and detects any motion after that. "
         "It also notifies the user that a motion has been detected by sending an email to the email address "
         "provided within the below input box.")
receiver_email = st.text_input("Enter your email address to test app!")
col3, col4 = st.columns(2)
with col3:
    start = st.button('Start Camera')
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

if start:
    if receiver_email == "":
        st.error("Please enter email first!")
    elif not re.fullmatch(regex, receiver_email):
        st.error("Please enter a valid email!")
    else:
        with col4:
            end = st.button("Stop Camera")

        streamlit_image = st.image([])

        video = cv2.VideoCapture(0)
        time.sleep(1)

        first_frame = None
        status_list = []
        count = 1

        while True:
            status = 0
            check, frame = video.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)

            if first_frame is None:
                first_frame = gray_frame_gau

            delta_frame = cv2.absdiff(first_frame, gray_frame_gau)

            thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]
            dilate_frame = cv2.dilate(thresh_frame, None, iterations=2)

            # cv2.imshow("My video", dilate_frame)

            contours, check = cv2.findContours(dilate_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                if cv2.contourArea(contour) < 5000:
                    continue
                x, y, w, h = cv2.boundingRect(contour)
                rect = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                if rect.any():
                    status = 1
                    cv2.imwrite(f"images/{count}.png", frame)
                    count = count + 1
                    all_images = glob.glob("images/*.png")
                    index = int(len(all_images) / 2)
                    image_with_object = all_images[index]

            status_list.append(status)
            status_list = status_list[-2:]

            if status_list[0] == 1 and status_list[1] == 0:
                email_thread = Thread(target=send_email, args=(image_with_object, receiver_email))
                email_thread.daemon = True
                email_thread.start()

            streamlit_image.image(frame)

clean_thread = Thread(target=clean_folder, )
clean_thread.daemon = True
clean_thread.start()

# with col2:

st.subheader("Instructions to try out the app:")
st.caption("""1. Enter your email or some temporary email to test the email.
2. Click on 'Start Camera' button and get a bit away from the camera.
3. Bring any object in front on the camera, once the camera caught an object which was not there initially, it will highlight that object with a rectangle.
4. Take that object back and click on the stop camera button.
5. Check the inbox of the email address you entered above, you must received an email saying that the motion has been detedted.
 <b>Note:</b> You might receive multiple emails while the camera is working if the camera caught multiple objects multiple times.""", unsafe_allow_html=True)

