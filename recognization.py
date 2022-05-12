import cv2
import os
import pandas as pd
import face_recognition
import FaceDetectionModule
import numpy as np
from datetime import datetime
import PySimpleGUI as Sg

Sg.theme("DarkAmber")
font = ('Consolas', 12, 'bold')
path = "ImageAttendance"
path_csv = 'AttendanceCSV/StudentList.csv'


def get_encoding(img_list):
    encode_list = []
    for item in img_list:
        cur_img = cv2.cvtColor(item, cv2.COLOR_BGR2RGB)
        cur_encode = face_recognition.face_encodings(cur_img)[0]
        encode_list.append(cur_encode)
    return encode_list


def mark_attendance(name):
    with open(path_csv, 'r+', encoding='UTF8', newline='') as f:
        data_list = f.readlines()
        name_list = []
        for line in data_list:
            entries = line.split(',')
            name_list.append(entries[0])
        if name not in name_list:
            now = datetime.now()
            date_time = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{date_time}')


def draw_name(frame, name, face_loc):
    if name == 'Unknown':
        y1, x2, y2, x1 = face_loc
        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), thickness=2)
        cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 0, 255), cv2.FILLED)
        cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.75, (255, 255, 255), thickness=2)
    else:
        y1, x2, y2, x1 = face_loc
        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), thickness=2)
        cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.75, (255, 255, 255), thickness=2)


def remove_specific_row_from_csv(file, column_name, *args):
    row_to_remove = []
    for row_name in args:
        row_to_remove.append(row_name)
    try:
        df = pd.read_csv(file)
        for row in row_to_remove:
            df = df[eval("df.{}".format(column_name)) != row]
        df.to_csv(file, index=False)
    except Exception:
        raise Exception("Error message....")


def remove_blanklines_csv(file):
    df = pd.read_csv(file)
    # Dropping the empty rows
    modified_df = df.dropna()
    # Saving it to the csv file
    modified_df.to_csv(file, index=False)


def get_student_data(file):
    remove_blanklines_csv(file)
    with open(file, 'r', encoding='UTF8', newline='') as f:
        data_list = f.readlines()
    return data_list[1:]


def face_recognizer(frame, detector, known_face_encodes, name_list):
    img_small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    faces = detector.findFaces(img_small)
    face_loc = []
    for face in faces:
        x, y, w, h = face[1]
        face_tuple = (y, x + w, y + h, x)
        face_loc.append(face_tuple)
    cur_frame_face_encodes = face_recognition.face_encodings(img_small, known_face_locations=face_loc)
    for encodeFace, faceLoc in zip(cur_frame_face_encodes, face_loc):
        face_dis = face_recognition.face_distance(known_face_encodes, encodeFace)
        match_idx = np.argmin(face_dis)
        if face_dis[match_idx] < 0.6:
            name = name_list[match_idx]
            mark_attendance(name)
        else:
            name = 'Unknown'
        draw_name(frame, name, faceLoc)
    return frame


def check_attendance():
    # Fields in attendance file
    with open(path_csv, 'w', encoding='UTF8', newline='') as f:
        f.writelines('Name,Arrival time')

    # Encode reference images
    images = []
    names = []
    my_list = os.listdir(path)
    for item in my_list:
        img = cv2.imread(f'{path}/{item}')
        images.append(img)
        names.append(os.path.splitext(item)[0])
    known_face_encodes = get_encoding(images)

    # Define layout
    webcam_column = [
        [Sg.Text("Live Webcam Feed", size=(60, 1), justification="center", font=font)],
        [Sg.Image(filename="", key="-IMAGE-")],
        [Sg.Button("Exit", size=(10, 1), font=font)]
    ]
    student_list_column = [
        [
            Sg.Text("List of students:", justification="center", font=font)
        ],
        [
            Sg.Listbox(values=[], enable_events=True, size=(80, 20), key="-FILE LIST-"),
        ],
        [
            Sg.Text("Number of present student:"),
            Sg.Text(text="", justification="center", font=font, key="-STU NUM-")
        ],
        [
            Sg.Text(text="", justification="left", font=font, size=(40, 1), key="-CHOSEN STU-",
                    background_color="#a2ff00", text_color="#151717"),
            Sg.Button("Uncheck", size=(10, 1), font=font),
            Sg.Button("Unselect", size=(10, 1), font=font)
        ]
    ]

    layout = [
        [
            Sg.Column(webcam_column),
            Sg.VSeperator(),
            Sg.Column(student_list_column)
        ]
    ]

    # Define window
    window = Sg.Window("Attendance Checking", layout, background_color="#8DDF5F", location=(200, 100))

    # Capture webcam feed
    cap = cv2.VideoCapture(0)
    detector = FaceDetectionModule.FaceDetector(model=1, minDetectionCon=0.6)

    # Event loop
    while True:
        event, values = window.read(timeout=20)
        ret, frame = cap.read()

        # User exceptions handling
        if not known_face_encodes:
            Sg.popup("No reference images!\nPlease register new student!", font=font)
            break

        if not ret:
            Sg.popup("No camera detected!", font=font)
            break

        # Buttons
        if event == "Exit" or event == Sg.WIN_CLOSED:
            break

        if event == "Uncheck":
            if window["-CHOSEN STU-"].DisplayText != "":
                remove_specific_row_from_csv(path_csv, "Name", window["-CHOSEN STU-"].DisplayText)
                window["-CHOSEN STU-"].update('')
            else:
                Sg.popup("Please choose student from the list to uncheck!", font=font)

        if event == "Unselect":
            window["-CHOSEN STU-"].update('')

        # Listbox
        if event == "-FILE LIST-":
            chosen_line = str(values["-FILE LIST-"][0])
            stu_info = chosen_line.split(sep=",")
            student_name = stu_info[0]
            window["-CHOSEN STU-"].update(student_name)

        # Update data
        stu_data = get_student_data(path_csv)
        window["-FILE LIST-"].update(stu_data)
        window["-STU NUM-"].update(str(len(stu_data)))  # Display the number of students

        frame = face_recognizer(frame=frame, detector=detector, known_face_encodes=known_face_encodes, name_list=names)
        img_bytes = cv2.imencode(".png", frame)[1].tobytes()
        window["-IMAGE-"].update(data=img_bytes)

    window.close()
    cap.release()
