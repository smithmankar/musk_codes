import pyautogui
import time
#manual scrolling

# Settings
target_image = 'invite_button.png'
confidence_level = 0.7
target_clicks = 500
click_count = 0
search_delay = 0.3  # how often to rescan screen

print(f"Clicking all '{target_image}' buttons until {target_clicks} total clicks...")

while click_count < target_clicks:
    try:
        # Find all current visible matches
        matches = list(pyautogui.locateAllOnScreen(target_image, confidence=confidence_level))

        if matches:
            print(f"[{click_count}] Found {len(matches)} match(es).")
            for match in matches:
                center = pyautogui.center(match)
                pyautogui.click(center)
                click_count += 1
                print(f"Clicked at {center} ({click_count}/{target_clicks})")
                time.sleep(0.2)  # short pause between clicks

                if click_count >= target_clicks:
                    break
        else:
            print(f"[{click_count}] No matches on screen. Waiting...")

        time.sleep(search_delay)

    except Exception as e:
        print(f"[ERROR] {e}")
        time.sleep(1)
