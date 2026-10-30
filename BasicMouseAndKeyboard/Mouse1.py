import pyautogui
import time

pyautogui.FAILSAFE = True
time.sleep(3)  # time to get ready

pyautogui.moveTo(500, 500, duration=1)   # glide to X=500, Y=500 over 1 second
pyautogui.moveTo(800, 500, duration=1)
pyautogui.moveTo(800, 800, duration=1)
pyautogui.moveTo(500, 800, duration=1)
print("Done!")

## this moves the mouse pointe in the desired coordinates according to the time