"""Python program to generate the following script:

 - a Tampermonkey script from a given configuration
 - Applescript to close tabs.

"""
from datetime import datetime
from typing import Mapping

import config
from config import (
    url_buttons_dict,
    url_query_dict
)


def generate_all_pattern_handling_config(mapping: Mapping):
    r"""Generate the configuration code for regex and button-finding logic as a config object.

    The format should look like this:
    const config = [
        {
            regex: /https:\/\/device\.sso\.*\.amazonaws\.com\/.*/,
            findButton: () => document.getElementById('cli_verification_btn')
        },
        {
            regex: /https:\/\/d-.*\.awsapps\.com\/start\/.*/,
            findButton: () => document.getElementById('cli_login_button') ||
                              document.querySelector('button[data-testid="allow-access-button"]')
        },
        ...
    ];
    """
    return "".join(generate_config_entry(
        p.replace("/", r"\/").replace(".", r"\.").replace("*", ".*"), q)
                   for p, q in mapping.items()).lstrip()


def generate_config_entry(pattern, queries):
    r"""Generate a single entry of the config object for the specified pattern and queries.

    The format of a config entry is:
    {
        regex: /<pattern>/,
        findButton: () => <button finding logic>
    }

    Example:
    {
        regex: /https:\/\/device\.sso\.*\.amazonaws\.com\/.*/,
        findButton: () => document.getElementById('cli_verification_btn')
    }
    """
    buttons = " ||\n".join(generate_button_finding_logic(query) for query in queries)
    return f"""
        {{
            regex: /{pattern}/,
            findButton: () => {buttons}
        }},
    """


def generate_button_finding_logic(query):
    """
    Generates the button finding logic for the findButton function in the config object.

    Example:
        document.getElementById('cli_verification_btn')

    In cases where multiple queries are provided, they will be combined with '||' to check multiple button conditions.
    """
    return query.lstrip().rstrip()


def generate_tampermonkey_script():
    # Get today's date in YYYY-MM-DD format
    today = datetime.now().strftime("%Y-%m-%d")

    # Generate the @include lines and URL-to-buttons mapping for the script
    includes = "\n".join([f"// @include      {pattern}" for pattern in url_buttons_dict])
    generated_config = generate_all_pattern_handling_config(url_buttons_dict)
    # Indent 4 more spaces
    generated_config = generated_config.replace("\n", "\n    ").rstrip()
    delay_ms = int(config.delay_seconds * 1000)

    # Generate the script with config-based pattern handling
    script = f"""// ==UserScript==
// @name         auto-web-login
// @namespace    http://tampermonkey.net/
// @version      {today}
// @description  Automatically click the buttons when doing web login
// @author       the.gigi@gmail.com
// @grant        none
{includes}
// ==/UserScript==

(function() {{
    'use strict';

    var maxAttempts = 20;
    var attempt = 0;

    function sleep(ms) {{
        return new Promise(resolve => setTimeout(resolve, ms));
    }}    

    async function handleButton(button) {{
        if (!button) {{
            return false;
        }}
        console.log('Found and clicked button');
        await sleep({delay_ms});
        button.click();
        return true;
    }}

    const config = [{generated_config}
    ];

    async function tryClickButtons() {{
        if (attempt >= maxAttempts) {{
            console.log("Max attempts reached. Stopping.");
            return;
        }}
        attempt++;
        console.log("Attempt:", attempt);
        var currentUrl = window.location.href;

        for (const {{ regex, findButton }} of config) {{
            if (regex.test(currentUrl)) {{
                const button = findButton();
                if (await handleButton(button)) {{
                    return;
                }}
            }}
        }}

        console.log("No button found, trying again in 1 second...");
        setTimeout(tryClickButtons, 1000); // Wait for 1 second before trying again        
    }}

    if (document.readyState === 'complete' || document.readyState === 'interactive') {{
        // If the document is already loaded or nearly loaded, call the function immediately
        tryClickButtons();
    }} else {{
        // Otherwise, wait for the load event
        window.addEventListener('load', tryClickButtons);
    }}
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
                set regexPattern to item 1 of pair
                set query to item 2 of pair
                -- Use shell script to perform regex matching
                set matched to do shell script "echo " & quoted form of currentURL & " | egrep -c " & quoted form of regexPattern
                if matched is not "0" then
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
