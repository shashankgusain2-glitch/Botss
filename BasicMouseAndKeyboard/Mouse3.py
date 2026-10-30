import pyautogui
import time

time.sleep(3)

for i in range(5):
    pyautogui.click(600, 400)
    print(f"Click number {i + 1}")
    time.sleep(0.5)

    ## in this cursoer goe sin for loop for a fixed time nad jumps to specific loacation each internval in this case it jumps back to sma eposition
    