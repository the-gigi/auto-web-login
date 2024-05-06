
set urlQueryPairs to {{"https://d-[a-zA-Z0-9-]*.awsapps.com/start/.*", "Array.from(document.querySelectorAll('div')).find(el => el.textContent === 'Request approved');"}}
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
