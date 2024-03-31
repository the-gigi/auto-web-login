""""Python script to generate a Tampermonkey script from a given configuration


"""
import json
from pprint import pprint
from datetime import datetime

from config import (
    url_buttons_dict,
    url_query_dict
)


def generate_tampermonkey_script():
    # Get today's date in YYYY-MM-DD format
    today = datetime.now().strftime("%Y-%m-%d")

    # Generate the @include lines and URL-to-buttons mapping for the script
    includes = "\n".join([f"// @include      {pattern}" for pattern in url_buttons_dict])
    mappings = json.dumps(url_buttons_dict, indent=12)
    # convert * wildcards to .* for regex
    mappings = mappings.replace("*", ".*")
    # adjust the indent on the last curly brace
    mappings = mappings[:-1] + ' ' * 8 + '}'

    script = f"""// ==UserScript==
// @name         auto-web-login
// @namespace    http://tampermonkey.net/
// @version      {today}
// @description  Automatically click the buttons when doing aws sso login
// @author       the.gigi@gmail.com
// @grant        none
{includes}
// ==/UserScript==

(function() {{
    'use strict';

    var maxAttempts = 5;
    var attempt = 0;

    function tryClickButtons() {{
        if (attempt >= maxAttempts) {{
            console.log("Max attempts reached. Stopping.");
            return;
        }}
        attempt++;
        console.log("Attempt:", attempt);

        var urlButtonMappings = {mappings};
        var currentUrl = window.location.href;

        var buttonClicked = false;
        Object.keys(urlButtonMappings).forEach(function(pattern) {{
            var regex = new RegExp(pattern);
            if (regex.test(currentUrl)) {{
                var buttonIds = urlButtonMappings[pattern];
                buttonIds.forEach(function(buttonId) {{
                    console.log('Trying button id: ' + buttonId);
                    var button = document.getElementById(buttonId);
                    if (button) {{
                        console.log('Found and clicked button id: ' + buttonId);
                        button.click();
                        buttonClicked = true;
                    }}
                }});
            }}
        }});

        if (!buttonClicked) {{
            console.log("No button found, trying again in 1 second...");
            setTimeout(tryClickButtons, 1000); // Wait for 1 second before trying again
        }}
    }}

    window.addEventListener('load', tryClickButtons);
}})();"""
    return script


def generate_applescript():
    # Convert final_page_url_query_dict into an AppleScript list dictionary
    url_query_pairs = "{" + ", ".join([f'{{"{k}", "{v}"}}' for k, v in url_query_dict.items()]) + "}"

    # AppleScript template with placeholders
    script = f"""
set urlQueryPairs to {url_query_pairs}
repeat
    tell application "Google Chrome"
        try
            set currentTab to active tab of front window
            set currentURL to URL of currentTab
            -- Check all pairs
            repeat with pair in urlQueryPairs
                set partialPath to item 1 of pair
                set query to item 2 of pair
                if (currentURL contains partialPath) then
                -- Construct the full JavaScript query correctly
                    set fullQuery to "var el = " & query & "; el ? 'found' : 'not found';"
                    set queryResult to execute currentTab javascript fullQuery
                    if queryResult is "found" then
                        delete currentTab
                        -- switch back to the terminal
                        tell application "iTerm2"
                            activate
                        end tell
                        exit repeat -- Exit the inner repeat loop if a match is found and tab is closed
                    end if
                end if
            end repeat

        on error errMsg
            -- Do nothing if there is an error.
        end try
    end tell
    delay 1 -- Delays for 1 second before the next iteration
end repeat
"""
    return script


def main():
    tampermonkey_script = generate_tampermonkey_script()
    apple_script = generate_applescript()

    open('auto_web_login.js', 'w').write(tampermonkey_script)
    open('CloseTabs.applescript', 'w').write(apple_script)


if __name__ == '__main__':
    main()
