import pyautogui
import time

time.sleep(3)

pyautogui.moveTo(600, 400, duration=1)
pyautogui.click()                 # one left click
time.sleep(1)
pyautogui.doubleClick()           # double click
time.sleep(1)
pyautogui.click(button="right")   # right click
print("Done!")