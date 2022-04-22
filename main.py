import PySimpleGUI as Sg
import recognization
import register_new_student
import os
import sys

Sg.theme("DarkAmber")
font = ('Consolas', 12, 'bold')

def change_directory():
    '''Change to runtime directory'''
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(__file__)
    os.chdir(application_path)


def main():
    change_directory()
    layout = [
        [Sg.Image(source="background theme/main_gui_theme.png")],
        [Sg.Button("Register New Student", size=(10, 2), font=font, expand_x=True), Sg.Button("Check Attendance", size=(10, 2), font=font, expand_x=True)],
        [Sg.Button("Quit", size=(10, 1), font=font, expand_x=True)]
    ]
    window = Sg.Window(title="Facial Attendance checking", layout=layout, background_color="#8DDF5F", element_justification="center", icon="background theme/ios_face_recognition_icon_155232.ico")
    while True:
        event, values = window.read()
        if event in (Sg.WIN_CLOSED, "Quit"):
            break

        if event == "Register New Student":
            register_new_student.register()

        if event == "Check Attendance":
            recognization.check_attendance()

    window.close()


if __name__ == '__main__':
    main()
