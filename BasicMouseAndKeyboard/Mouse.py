import pyautogui
import time

print("Move your mouse around. Press Ctrl+C to stop.")
try:
    while True:
        x, y = pyautogui.position()
        print(f"Mouse is at X={x}, Y={y}")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Stopped.")