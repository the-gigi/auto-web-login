""""Python script to generate a Tampermonkey script from a given configuration


"""
import json
from pprint import pprint
from datetime import datetime
from typing import Dict, Mapping

from config import (
    url_buttons_dict,
    url_query_dict
)


def generate_all_pattern_handling_code(mapping: Mapping):
    """
    The format of all pattern handling code is:

    <pattern handling code>
    <pattern handling code>
    ...
    <pattern handling code>

    Need to change wildcard form the mapping (*) to regex wildcard (.*)

    Example:

    regex = new RegExp("https://device.sso..*.amazonaws.com/.*");
    if (regex.test(currentUrl)) {
        button = document.getElementById("cli_verification_btn");
        if (handleButton(button)) {
            return;
        }
    }

    regex = new RegExp("https://d-.*.awsapps.com/start/.*");
    if (regex.test(currentUrl)) {
        button = document.getElementById("cli_login_button");
        if (handleButton(button)) {
            return;
        }
    }
    """
    return "".join(generate_pattern_handling_code(p.replace("*", ".*"), q)
                   for p, q in mapping.items()).lstrip()


def generate_pattern_handling_code(pattern, queries):
    """
    The format of a pattern handling code is:

    regex = new RegExp("<pattern>");
    if (regex.test(currentUrl)) {{
        <button handling code>
        <button handling code>
        ...
        <button handling code>
    }}

    Example:

    regex = new RegExp("https://device.sso..*.amazonaws.com/.*");
    if (regex.test(currentUrl)) {{
        button = document.getElementById("cli_verification_btn");
        if (handleButton(button)) {{
            return;
        }}
    }}

    """

    buttons = "\n".join(generate_button_handling_code(query) for query in queries)
    return f"""
    regex = new RegExp("{pattern}");
    if (regex.test(currentUrl)) {{
        {buttons.lstrip()}
    }}    
    """


def generate_button_handling_code(query):
    """
    The format of a pattern handling code is:

    button = <query>;
    if (handleButton(button)) {{
        return;
    }}

    Example:

    button = document.getElementById("cli_verification_btn");
    if (handleButton(button)) {{
        return;
    }}
    """
    return f"""
        button = {query};
        if (handleButton(button)) {{
            return;
        }}
    """[1:].rstrip()


def generate_tampermonkey_script():
    # Get today's date in YYYY-MM-DD format
    today = datetime.now().strftime("%Y-%m-%d")

    # Generate the @include lines and URL-to-buttons mapping for the script
    includes = "\n".join([f"// @include      {pattern}" for pattern in url_buttons_dict])
    generated_code = generate_all_pattern_handling_code(url_buttons_dict)
    # Indent 4 more spaces
    generated_code = generated_code.replace("\n", "\n    ").rstrip()

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

    function handleButton(button) {{
        if (!button) {{
            return false;
        }}
        console.log('Found and clicked button');
        button.click();
        return true;
    }}

    function tryClickButtons() {{
        if (attempt >= maxAttempts) {{
            console.log("Max attempts reached. Stopping.");
            return;
        }}
        attempt++;
        console.log("Attempt:", attempt);
        var currentUrl = window.location.href;
        var buttonClicked = false;
        var regex = null;
        var button = null;
        
        {generated_code} 
               
        console.log("No button found, trying again in 1 second...");
        setTimeout(tryClickButtons, 1000); // Wait for 1 second before trying again        
    }}

    window.addEventListener('load', tryClickButtons);
}})();
"""
    lines = script.split("\n")
    lines = [line.rstrip() for line in lines]
    return "\n".join(lines)


def generate_applescript():
    # Convert final_page_url_query_dict into an AppleScript list dictionary
    url_query_pairs = "{" + ", ".join(
        [f'{{"{k}", "{v}"}}' for k, v in url_query_dict.items()]) + "}"

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
    lines = script.split("\n")
    lines = [line.rstrip() for line in lines]
    return "\n".join(lines)


def main():
    tampermonkey_script = generate_tampermonkey_script()
    apple_script = generate_applescript()

    open('auto_web_login.js', 'w').write(tampermonkey_script)
    open('CloseTabs.applescript', 'w').write(apple_script)


if __name__ == '__main__':
    main()
