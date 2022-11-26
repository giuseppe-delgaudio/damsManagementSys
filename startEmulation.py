import subprocess

subprocess.Popen(["py","asset/startSensorsEmulation.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)
subprocess.Popen(["py","asset/emulateDam.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)
