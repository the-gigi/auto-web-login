import time

import pyautogui
from pyautogui import Point
import sh
from config import user_click_dict


def osascript(script):
    """Execute an AppleScript command via the osascript command-line tool.

    Parameters:
        script (str): A string containing the AppleScript code to execute.

    Returns:
        str: The output from the executed script as a string.
    """
    return sh.osascript('-e', script)


def get_absolute_viewport_top():
    """Retrieves the absolute top position of the viewport of the active tab in Google Chrome.

    This function calculates the viewport top by executing JavaScript in Chrome via AppleScript.
    It determines the distance from the top of the screen to the inside top of the browser window.

    Returns:
        int: The absolute top position of the viewport.
    """
    cmd = """
        tell application "Google Chrome"
            tell the active tab of window 1
                set js to "window.screenY + window.outerHeight - window.innerHeight"
                set viewportTop to execute javascript js
                return viewportTop
            end tell
        end tell
    """
    res = osascript(cmd)
    return int(res)


def get_chrome_origin():
    """Fetches the x,y position and size of top-left corner of the foremost Google Chrome window.

    This function uses AppleScript to interact with System Events to retrieve the position
    of the first window of Google Chrome in absolute screen coordinates.

    Returns:
        list: A list containing four integers [x, y, width, height] that define the bounding rect
    """
    cmd = """
        tell application "System Events" to tell process "Google Chrome"
            set thePos to position of first window
            return thePos
        end tell
    """
    res = osascript(cmd)
    return Point(*[int(item.strip()) for item in res.split(',')])


def find_element_center(partial_url, query):
    """
    This function is designed to find the center coordinates of an element in Google Chrome by
    executing a JavaScript query on the active tab if its URL contains a specific partial URL.
    In the viewport coordinate system

    Parameters:
        partial_url (str): The URL or a part of it to locate the correct tab.
        query (str): JavaScript code as a string to find and possibly interact with the element.

    Returns:
        tuple: The center (x, y) coordinates of the found element, or None if not found
    """
    # Properly escape the query to ensure it's treated as a literal string in AppleScript
    escaped_query = query.replace('"', '\\"')
    # Adjust the JavaScript to find the bounding rectangle and calculate the center
    full_query = f"var el = {escaped_query}; if (el) {{ var rect = el.getBoundingClientRect(); var centerX = rect.left + rect.width / 2; var centerY = rect.top + rect.height / 2; centerX + ',' + centerY; }} else {{ 'not found'; }}"
    escaped_url = partial_url.replace('"', '\\"')

    cmd = f"""
        tell application "Google Chrome"
            try
                set currentTab to the active tab of the front window
                set currentURL to the URL of currentTab

                if currentURL contains "{escaped_url}" then
                    -- Construct and execute the JavaScript query to find the center of the element
                    set fullQuery to "{full_query}"
                    set queryResult to execute currentTab javascript fullQuery
                    return queryResult
                else
                    return "URL does not contain the specified partial URL."
                end if
            on error errMsg
                return "An error occurred: " & errMsg
            end try
        end tell
    """
    res = osascript(cmd)
    # Parse the result, assuming it's a string of "x,y" or an error message
    if ',' not in res:
        return None, None

    x, y = res.split(',')
    return float(x.strip()), float(y.strip())


def click_element(partial_url, query):
    # Calculate the relative position of the element (viewport coordinate)
    dx, dy = find_element_center(partial_url, query)
    if dx is None:
        return

    # Calculate the absolute position of the viewport
    x, y = get_chrome_origin()
    y = get_absolute_viewport_top()

    # Translate the element center to absolute coordinates
    x += dx
    y += dy

    # Move the mouse to the center of the element and click twice (in case need to get focus first)
    pyautogui.moveTo(x, y)
    pyautogui.click()
    pyautogui.click()


def main():
    while True:
        for partial_url, query in user_click_dict.items():
            click_element(partial_url, query)
        time.sleep(3)


if __name__ == '__main__':
    main()
