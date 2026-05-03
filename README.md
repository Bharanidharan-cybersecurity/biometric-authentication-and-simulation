          Biometric Face Recognition System
Technologies Used:
* Python
* OpenCV (Face Recognition)
* NumPy
* Tkinter (GUI)
* PIL (Image Processing)
* pyttsx3 (Text-to-Speech)

Do it in shell !
First think check if the python version is 3.11 or install 3.11 using the command:
```bash
winget install Python.Python.3.11
py -0       
```
Now follow the steps to setup the environment:
```bash
cd C:\Users\bhara\Music\biometric
py -3.11 -m venv .venv
.venv\Scripts\activate
```
--------------------------------------------------------------------------
if the activate of .venv is not working do this!
```bash
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
```
--------------------------------------------------------------------------

Required Packages:

Install the following dependencies before running the project:

```bash
pip install numpy pillow pyttsx3
pip install opencv-contrib-python
