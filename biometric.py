import cv2
import os
import numpy as np
from PIL import Image
import tkinter as tk
import webbrowser
import pyttsx3

# ---------- VOICE ----------
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# ---------- USER STORAGE ----------
user_map = {}
pin_map = {}

# ---------- LOAD USERS ----------
if os.path.exists("users.txt"):

    with open("users.txt", "r") as f:

        for line in f:

            parts = line.strip().split(",")

            # uid,name,pin
            if len(parts) == 3:

                uid, uname, upin = parts

                user_map[int(uid)] = uname
                pin_map[int(uid)] = upin


# ---------- APP CLASS ----------
class App:

    def __init__(self, root):

        self.root = root
        self.root.title("Biometric Authentication System")
        self.root.geometry("380x700")
        self.root.configure(bg="#0f172a")

        self.main_frame = tk.Frame(root, bg="#0f172a")
        self.main_frame.pack(fill="both", expand=True)

        self.create_login_screen()

    # ---------- CLEAR SCREEN ----------
    def clear(self):

        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ---------- BUTTON ----------
    def create_button(self, text, color, command):

        return tk.Button(
            self.main_frame,
            text=text,
            bg=color,
            fg="white",
            font=("Arial", 12, "bold"),
            width=25,
            height=2,
            bd=0,
            command=command
        )

    # ---------- STATUS ----------
    def update_status(self, msg, color):

        self.status.config(text=msg, fg=color)
        self.root.update_idletasks()

    # ---------- LOGIN SCREEN ----------
    def create_login_screen(self):

        self.clear()

        tk.Label(
            self.main_frame,
            text="Biometric Login",
            font=("Arial", 22, "bold"),
            bg="#0f172a",
            fg="white"
        ).pack(pady=20)

        card = tk.Frame(
            self.main_frame,
            bg="#1e293b",
            padx=20,
            pady=20
        )

        card.pack(pady=10)

        # USER ID
        tk.Label(
            card,
            text="User ID",
            bg="#1e293b",
            fg="white"
        ).pack(anchor="w")

        self.entry_id = tk.Entry(card)
        self.entry_id.pack(pady=5, fill="x")

        # USERNAME
        tk.Label(
            card,
            text="Username",
            bg="#1e293b",
            fg="white"
        ).pack(anchor="w")

        self.entry_name = tk.Entry(card)
        self.entry_name.pack(pady=5, fill="x")

        # PIN
        tk.Label(
            card,
            text="PIN",
            bg="#1e293b",
            fg="white"
        ).pack(anchor="w")

        self.entry_pin = tk.Entry(card, show="*")
        self.entry_pin.pack(pady=5, fill="x")

        self.status = tk.Label(
            self.main_frame,
            text="Ready",
            bg="#0f172a",
            fg="#4ade80",
            font=("Arial", 11, "bold")
        )

        self.status.pack(pady=10)

        self.create_button(
            "Register Face",
            "#22c55e",
            self.register
        ).pack(pady=8)

        self.create_button(
            "Train Model",
            "#3b82f6",
            self.train_model
        ).pack(pady=8)

        self.create_button(
            "Login",
            "#f59e0b",
            self.login
        ).pack(pady=8)

    # ---------- DASHBOARD ----------
    def create_dashboard(self, name):

        self.clear()

        tk.Label(
            self.main_frame,
            text="Dashboard",
            font=("Arial", 22, "bold"),
            bg="#0f172a",
            fg="white"
        ).pack(pady=20)

        tk.Label(
            self.main_frame,
            text=f"Welcome, {name}",
            font=("Arial", 15),
            bg="#0f172a",
            fg="#4ade80"
        ).pack(pady=10)

        self.create_button(
            "Open College Portal",
            "#3b82f6",
            lambda: webbrowser.open(
                "https://portal.shanmugha.edu.in/"
            )
        ).pack(pady=10)

        self.create_button(
            "Logout",
            "#ef4444",
            self.create_login_screen
        ).pack(pady=10)

    # ---------- REGISTER ----------
    def register(self):

        uid = self.entry_id.get()
        name = self.entry_name.get()
        pin = self.entry_pin.get()

        # VALIDATION
        if uid == "" or name == "" or pin == "":

            self.update_status(
                "Fill all fields",
                "red"
            )

            return

        if not uid.isdigit():

            self.update_status(
                "User ID must be number",
                "red"
            )

            return

        uid = int(uid)

        # SAVE USER
        user_map[uid] = name
        pin_map[uid] = pin

        with open("users.txt", "a") as f:

            f.write(f"{uid},{name},{pin}\n")

        cam = cv2.VideoCapture(0)

        if not cam.isOpened():

            self.update_status(
                "Camera Error",
                "red"
            )

            return

        detector = cv2.CascadeClassifier(
            cv2.data.haarcascades +
            "haarcascade_frontalface_default.xml"
        )

        os.makedirs("dataset", exist_ok=True)

        count = 0

        self.update_status(
            "Scanning Face...",
            "yellow"
        )

        while True:

            ret, img = cam.read()

            if not ret:
                break

            gray = cv2.cvtColor(
                img,
                cv2.COLOR_BGR2GRAY
            )

            faces = detector.detectMultiScale(
                gray,
                1.3,
                5
            )

            for (x, y, w, h) in faces:

                count += 1

                face = gray[y:y+h, x:x+w]

                cv2.imwrite(
                    f"dataset/User.{uid}.{count}.jpg",
                    face
                )

                cv2.rectangle(
                    img,
                    (x, y),
                    (x+w, y+h),
                    (0, 255, 255),
                    2
                )

            cv2.imshow("Face Registration", img)

            # ESC OR 20 IMAGES
            if cv2.waitKey(1) == 27 or count >= 20:
                break

        cam.release()
        cv2.destroyAllWindows()

        self.update_status(
            "Registration Complete ✔",
            "#4CAF50"
        )

        engine.say("Face Registered Successfully")
        engine.runAndWait()

    # ---------- TRAIN MODEL ----------
    def train_model(self):

        if not os.path.exists("dataset"):

            self.update_status(
                "No dataset found",
                "red"
            )

            return

        recognizer = cv2.face.LBPHFaceRecognizer_create()

        detector = cv2.CascadeClassifier(
            cv2.data.haarcascades +
            "haarcascade_frontalface_default.xml"
        )

        faces = []
        ids = []

        for file in os.listdir("dataset"):

            path = os.path.join("dataset", file)

            img = Image.open(path).convert('L')

            img_np = np.array(img, 'uint8')

            uid = int(file.split(".")[1])

            detected_faces = detector.detectMultiScale(img_np)

            for (x, y, w, h) in detected_faces:

                faces.append(img_np[y:y+h, x:x+w])
                ids.append(uid)

        if len(faces) == 0:

            self.update_status(
                "No faces detected",
                "red"
            )

            return

        recognizer.train(
            faces,
            np.array(ids)
        )

        recognizer.write("trainer.yml")

        self.update_status(
            "Model Trained ✔",
            "#4CAF50"
        )

        engine.say("Training Completed")
        engine.runAndWait()

    # ---------- LOGIN ----------
    def login(self):

        if not os.path.exists("trainer.yml"):

            self.update_status(
                "Train model first",
                "red"
            )

            return

        recognizer = cv2.face.LBPHFaceRecognizer_create()

        recognizer.read("trainer.yml")

        detector = cv2.CascadeClassifier(
            cv2.data.haarcascades +
            "haarcascade_frontalface_default.xml"
        )

        cam = cv2.VideoCapture(0)

        if not cam.isOpened():

            self.update_status(
                "Camera Error",
                "red"
            )

            return

        self.update_status(
            "Authenticating...",
            "yellow"
        )

        attempts = 0

        while True:

            ret, img = cam.read()

            if not ret:
                break

            gray = cv2.cvtColor(
                img,
                cv2.COLOR_BGR2GRAY
            )

            faces = detector.detectMultiScale(
                gray,
                1.3,
                5
            )

            for (x, y, w, h) in faces:

                uid, conf = recognizer.predict(
                    gray[y:y+h, x:x+w]
                )

                # ---------- FACE MATCH ----------
                if conf < 70:

                    entered_pin = self.entry_pin.get()

                    saved_pin = pin_map.get(uid)

                    # ---------- PIN CHECK ----------
                    if entered_pin == saved_pin:

                        name = user_map.get(
                            uid,
                            f"User {uid}"
                        )

                        self.update_status(
                            f"Welcome {name}",
                            "#4CAF50"
                        )

                        engine.say(
                            f"Welcome {name}"
                        )

                        engine.runAndWait()

                        cam.release()
                        cv2.destroyAllWindows()

                        self.create_dashboard(name)

                        return

                    else:

                        self.update_status(
                            "Wrong PIN",
                            "red"
                        )

                        engine.say(
                            "Wrong PIN"
                        )

                        engine.runAndWait()

                        cam.release()
                        cv2.destroyAllWindows()

                        return

                # ---------- UNKNOWN PERSON ----------
                else:

                    attempts += 1

                    self.update_status(
                        "Access Denied",
                        "red"
                    )

                    # SAVE INTRUDER IMAGE
                    os.makedirs(
                        "intruders",
                        exist_ok=True
                    )

                    cv2.imwrite(
                        f"intruders/intruder_{attempts}.jpg",
                        img
                    )

                    engine.say(
                        "Access Denied"
                    )

                    engine.runAndWait()

                    # EXIT AFTER 3 ATTEMPTS
                    if attempts >= 3:

                        engine.say(
                            "Application Closing"
                        )

                        engine.runAndWait()

                        cam.release()
                        cv2.destroyAllWindows()

                        self.root.destroy()

                        return

            cv2.imshow("Face Authentication", img)

            # ESC KEY
            if cv2.waitKey(1) == 27:
                break

        cam.release()
        cv2.destroyAllWindows()


# ---------- RUN ----------
root = tk.Tk()

app = App(root)

root.mainloop()