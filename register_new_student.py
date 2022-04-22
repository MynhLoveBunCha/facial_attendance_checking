import cv2
import PySimpleGUI as Sg
import os


def register():
    Sg.theme("DarkAmber")
    path = "ImageAttendance"
    font = ('Consolas', 12, 'bold')
    # Define the window layout
    webcam_column = [
        [Sg.Text("Live Webcam Feed", size=(60, 1), justification="center", font=font)],
        [Sg.Image(filename="", key="-IMAGE-")],
        [Sg.Text("Enter student name: ", font=font), Sg.Input(key="-INPUT-", font=('Consolas', 10, 'bold')), Sg.Button("Clear", font=font)],
        [Sg.Button("Snap", size=(10, 1), font=font), Sg.Button("Exit", size=(10, 1), font=font)],
    ]

    file_list_column = [
        [
            Sg.Text("List of reference images:", justification="center", font=font)
        ],
        [
            Sg.Listbox(values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"),
        ]
    ]

    image_viewer_column = [
        [Sg.Text("Choose an image from the list on the left:", font=font)],
        [Sg.Text(size=(40, 1), key="-TOUT-", font=font)],
        [Sg.Image(key="-VIEW IMAGE-")],
        [Sg.Button("Delete", size=(10, 1), font=font), Sg.Button("Keep", size=(10, 1), font=font)]
    ]

    layout = [
        [
            Sg.Column(webcam_column),
            Sg.VSeperator(),
            Sg.Column(file_list_column),
            Sg.VSeperator(),
            Sg.Column(image_viewer_column)
        ]
    ]
    # Create the window
    main_window = Sg.Window("Register New Student", layout, background_color="#8DDF5F", location=(200, 100))

    # Capture webcam feed
    cap = cv2.VideoCapture(0)

    # Event loop
    while True:
        main_event, main_values = main_window.read(timeout=20)
        ret, frame = cap.read()

        if not ret:
            Sg.popup("No camera detected!", font=font)
            break

        if main_event == "Exit" or main_event == Sg.WIN_CLOSED:
            break
        file_list = os.listdir(path)
        file_names = [
            f
            for f in file_list
            if os.path.isfile(os.path.join(path, f))
            and f.lower().endswith((".png", ".gif"))
        ]
        main_window["-FILE LIST-"].update(file_names)
        if main_event == "-FILE LIST-":
            filename = os.path.join(
                path, main_values["-FILE LIST-"][0]
            )
            main_window["-TOUT-"].update(filename)
            main_window["-VIEW IMAGE-"].update(filename=filename)

        if main_event == "Keep":
            main_window["-TOUT-"].update('')
            main_window["-VIEW IMAGE-"].update('')

        if main_event == "Delete":
            try:
                if main_window["-FILE LIST-"].Values:
                    os.remove(main_window["-TOUT-"].DisplayText)
                    main_window["-TOUT-"].update('')
                    main_window["-VIEW IMAGE-"].update('')
                else:
                    Sg.popup("No images found!", font=font)
            except FileNotFoundError:
                Sg.popup("Please choose image to delete!", font=font)

        if main_event == "Snap":
            if main_values["-INPUT-"] == "":
                Sg.popup("Please enter your name!", font=font)
            else:
                img_popup = cv2.imencode(".png", frame)[1].tobytes()
                if Sg.PopupYesNo("Do you wish to save the image?", image=img_popup, font=font) == "Yes":
                    img_name = "{}.png".format(main_values["-INPUT-"])
                    cv2.imwrite(path + "/" + img_name, frame)
                    Sg.popup("{} has been saved in {} folder!".format(img_name, path), font=font)
        if main_event == "Clear":
            main_window['-INPUT-'].update('')
        img_bytes = cv2.imencode(".png", frame)[1].tobytes()
        main_window["-IMAGE-"].update(data=img_bytes)

    main_window.close()
    cap.release()
