import cv2
import os
import numpy as np #image data processing
from PIL import Image #image handling
import tkinter as tk
import webbrowser
import pyttsx3  #text to speech

# ---------- VOICE ----------
engine = pyttsx3.init()
engine.setProperty('rate', 150)

user_map = {}

# ---------- LOAD USERS ----------
if os.path.exists("users.txt"):
    with open("users.txt", "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) == 2:
                uid, uname = parts
                user_map[int(uid)] = uname

# ---------- APP CLASS ----------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Biometric App")
        self.root.geometry("360x640")
        self.root.configure(bg="#0f172a")

        self.main_frame = tk.Frame(root, bg="#0f172a")
        self.main_frame.pack(fill="both", expand=True)

        self.create_login_screen()

    def clear(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ---------- LOGIN UI ----------
    def create_login_screen(self):
        self.clear()

        tk.Label(self.main_frame, text="Biometric Login",
                 font=("Arial", 20, "bold"),
                 bg="#0f172a", fg="white").pack(pady=20)

        card = tk.Frame(self.main_frame, bg="#1e293b", padx=20, pady=20)
        card.pack(pady=10)

        tk.Label(card, text="User ID", bg="#1e293b", fg="white").pack(anchor="w")
        self.entry_id = tk.Entry(card)
        self.entry_id.pack(pady=5, fill="x")

        tk.Label(card, text="Username", bg="#1e293b", fg="white").pack(anchor="w")
        self.entry_name = tk.Entry(card)
        self.entry_name.pack(pady=5, fill="x")

        self.status = tk.Label(self.main_frame, text="Ready",
                               bg="#0f172a", fg="#4ade80")
        self.status.pack(pady=10)

        self.create_button("Register Face", "#22c55e", self.register).pack(pady=6)
        self.create_button("Train Model", "#3b82f6", self.train_model).pack(pady=6)
        self.create_button("Login", "#f59e0b", self.login).pack(pady=6)

    # ---------- DASHBOARD ----------
    def create_dashboard(self, name):
        self.clear()

        tk.Label(self.main_frame, text="Dashboard",
                 font=("Arial", 20, "bold"),
                 bg="#0f172a", fg="white").pack(pady=20)

        tk.Label(self.main_frame, text=f"Welcome, {name}",
                 font=("Arial", 14),
                 bg="#0f172a", fg="#4ade80").pack(pady=10)

        self.create_button("Open Portal", "#3b82f6",
                           lambda: webbrowser.open("https://portal.shanmugha.edu.in/")).pack(pady=10)

        self.create_button("Logout", "#ef4444",
                           self.create_login_screen).pack(pady=10)

    def create_button(self, text, color, command):
        return tk.Button(self.main_frame, text=text,
                         bg=color, fg="white",
                         font=("Arial", 12, "bold"),
                         width=25, height=2,
                         bd=0, command=command)

    def update_status(self, msg, color):
        self.status.config(text=msg, fg=color)
        self.root.update_idletasks()

    # ---------- REGISTER ----------
    def register(self):
        uid = self.entry_id.get()
        name = self.entry_name.get()

        if uid == "" or name == "":
            self.update_status("Fill all fields", "red")
            return

        user_map[int(uid)] = name

        with open("users.txt", "a") as f:
            f.write(f"{uid},{name}\n")

        cam = cv2.VideoCapture(0)

        if not cam.isOpened():
            self.update_status("Camera Error", "red")
            return

        detector = cv2.CascadeClassifier(cv2.data.haarcascades +
                                         "haarcascade_frontalface_default.xml")

        os.makedirs("dataset", exist_ok=True)
        count = 0

        self.update_status("Scanning...", "yellow")

        while True:
            ret, img = cam.read()
            if not ret:
                break

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                count += 1
                face = gray[y:y+h, x:x+w]
                cv2.imwrite(f"dataset/User.{uid}.{count}.jpg", face)
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 255), 2)

            cv2.imshow("Register", img)

            if cv2.waitKey(1) == 27 or count >= 20:
                break

        cam.release()
        cv2.destroyAllWindows()

        self.update_status("Registered ✔", "#4CAF50")

    # ---------- TRAIN ----------
    def train_model(self):
        if not os.path.exists("dataset"):
            self.update_status("No data", "red")
            return

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        detector = cv2.CascadeClassifier(cv2.data.haarcascades +
                                         "haarcascade_frontalface_default.xml")

        faces, ids = [], []

        for file in os.listdir("dataset"):
            path = os.path.join("dataset", file)
            img = Image.open(path).convert('L')
            img_np = np.array(img, 'uint8')

            id = int(file.split(".")[1])
            detected_faces = detector.detectMultiScale(img_np)

            for (x, y, w, h) in detected_faces:
                faces.append(img_np[y:y+h, x:x+w])
                ids.append(id)

        if len(faces) == 0:
            self.update_status("No faces found", "red")
            return

        recognizer.train(faces, np.array(ids))
        recognizer.write("trainer.yml")

        self.update_status("Model Ready ✔", "#4CAF50")

    # ---------- LOGIN ----------
    def login(self):
        if not os.path.exists("trainer.yml"):
            self.update_status("Train first", "red")
            return

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("trainer.yml")

        detector = cv2.CascadeClassifier(cv2.data.haarcascades +
                                         "haarcascade_frontalface_default.xml")

        cam = cv2.VideoCapture(0)

        if not cam.isOpened():
            self.update_status("Camera Error", "red")
            return

        self.update_status("Authenticating...", "yellow")

        while True:
            ret, img = cam.read()
            if not ret:
                break

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                id, conf = recognizer.predict(gray[y:y+h, x:x+w])

                if conf < 70:
                    name = user_map.get(id, f"User {id}")

                    self.update_status(f"Welcome {name}", "#4CAF50")

                    engine.say(f"Welcome {name}")
                    engine.runAndWait()

                    cam.release()
                    cv2.destroyAllWindows()

                    self.create_dashboard(name)
                    return
                else:
                    self.update_status("Denied", "red")

            cv2.imshow("Login", img)

            if cv2.waitKey(1) == 27:
                break

        cam.release()
        cv2.destroyAllWindows()


# ---------- RUN ----------
root = tk.Tk()
app = App(root)
root.mainloop()