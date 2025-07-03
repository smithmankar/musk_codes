import time
from pynput.mouse import Controller as MouseController
from pynput.mouse import Button
import pyautogui

# === Settings ===
target_image = 'invite_button.png'
confidence_level = 0.7
target_clicks = 600
click_count = 0
scroll_delay = 0.3
click_delay = 0.1
scroll_amount = -3  # -3 = 3 "clicks" down, adjust as needed

mouse = MouseController()

print(f"Starting... Looking for '{target_image}' until {target_clicks} clicks are completed.")
print("Place your mouse over the scrollable area before starting.")
time.sleep(2)

while click_count < target_clicks:
    try:
        # Always scroll on every loop at the current mouse position
        mouse.scroll(0, scroll_amount)
        print(f"[{click_count}] Scrolled by {scroll_amount} steps at mouse position {mouse.position}")
        time.sleep(scroll_delay)

        # Check for target image
        matches = list(pyautogui.locateAllOnScreen(target_image, confidence=confidence_level))

        if matches:
            print(f"[{click_count}] Found {len(matches)} button(s).")
            for match in matches:
                center = pyautogui.center(match)
                pyautogui.click(center)
                click_count += 1
                print(f"Clicked at {center} ({click_count}/{target_clicks})")
                time.sleep(click_delay)

                if click_count >= target_clicks:
                    print("Target clicks reached. Exiting.")
                    exit(0)
        else:
            print(f"[{click_count}] No buttons found this iteration, scrolling again...")

    except KeyboardInterrupt:
        print("Stopped by user.")
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(1)
