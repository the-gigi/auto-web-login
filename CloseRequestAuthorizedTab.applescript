repeat
    tell application "Google Chrome"
        try
            set currentTab to active tab of front window
            if (URL of currentTab ends with "awsapps.com/start/user-consent/login-success.html") then
                delete currentTab
                -- switch back to the terminal
                tell application "iTerm2"
                    activate
                end tell
                -- Removed exit repeat to keep running
            end if
        on error errMsg
            -- Do nothing if there is error.
        end try
    end tell
    delay 1 -- Delays for 1 second before the next iteration
end repeat
