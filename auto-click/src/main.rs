use enigo::{Enigo, Button, Mouse, Settings};
use std::process::Command;
use std::thread;
use std::time::Duration;
use serde::{Deserialize, Serialize};
use std::fs;
use std::error::Error;
use enigo::Coordinate::Abs;
use enigo::Direction::Click;

#[derive(Serialize, Deserialize, Debug)]
struct ClickConfig {
    url: String,
    query: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct Config {
    clicks: Vec<ClickConfig>,
}

fn load_click_config() -> Result<Vec<ClickConfig>, Box<dyn Error>> {
    // Get the config filename
    let home_dir = dirs::home_dir().ok_or("Unable to find the home directory")?;
    let config_file = home_dir.join(".auto-click/config.yaml");

    // Read the entire file as a string
    let data = fs::read_to_string(config_file)?;

    // Parse the string as YAML
    let config: Config = serde_yaml::from_str(&data)?;
    Ok(config.clicks)
}

fn osascript(script: &str) -> Result<String, Box<dyn std::error::Error>> {
    let output = Command::new("osascript")
        .arg("-e")
        .arg(script)
        .output()?;

    if output.status.success() {
        Ok(String::from_utf8(output.stdout)?)
    } else {
        Err(format!("Error executing AppleScript: {}", String::from_utf8(output.stderr)?).into())
    }
}

fn get_absolute_viewport_top() -> Result<i32, Box<dyn std::error::Error>> {
    let script = r#"
        tell application "Google Chrome"
        activate
            tell application "System Events"
                keystroke "0" using {command down}
            end tell
            tell the active tab of window 1
                set js to "window.screenY + window.outerHeight - window.innerHeight"
                set viewportTop to execute javascript js
                return viewportTop
            end tell
        end tell
    "#;
    let res = osascript(script)?;
    res.trim().parse::<i32>().map_err(Into::into)
}

fn get_chrome_origin() -> Result<(i32, i32), Box<dyn std::error::Error>> {
    let script = r#"
        tell application "System Events" to tell process "Google Chrome"
            set thePos to position of first window
            return thePos
        end tell
    "#;
    let res = osascript(script)?;
    let coords: Vec<i32> = res.split(',')
        .map(|s| s.trim().parse().unwrap())
        .collect();
    Ok((coords[0], coords[1]))
}

fn find_element_center(partial_url: &str, query: &str) -> Result<(f64, f64), Box<dyn std::error::Error>> {
    let escaped_query = query.replace("\"", "\\\"");
    let full_query = format!(
        "var el = {}; if (el) {{ var rect = el.getBoundingClientRect(); var centerX = rect.left + rect.width / 2; var centerY = rect.top + rect.height / 2; centerX + ',' + centerY; }} else {{ 'not found'; }}",
        escaped_query
    );
    let escaped_url = partial_url.replace("\"", "\\\"");
    let script = format!(r#"
        tell application "Google Chrome"
            try
                set currentTab to the active tab of the front window
                set currentURL to the URL of currentTab

                if currentURL contains "{}" then
                    -- Construct and execute the JavaScript query to find the center of the element
                    set fullQuery to "{}"
                    set queryResult to execute currentTab javascript fullQuery
                    return queryResult
                else
                    return "URL does not contain the specified partial URL."
                end if
            on error errMsg
                return "An error occurred: " & errMsg
            end try
        end tell
    "#, escaped_url, full_query);

    let res = osascript(&script)?;
    if res.contains(",") {
        let parts: Vec<&str> = res.split(',').collect();
        let x = parts[0].trim().parse::<f64>()?;
        let y = parts[1].trim().parse::<f64>()?;
        Ok((x, y))
    } else {
        Err("Element not found or error occurred".into())
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    //let chrome_origin = get_chrome_origin()?;
    //println!("Chrome origin: ({}, {})", chrome_origin.0, chrome_origin.1);
    let mut enigo = Enigo::new(&Settings::default()).unwrap();
    let user_click_dict = load_click_config()?;
    loop {
        for click in &user_click_dict {
            if let Ok((dx, dy)) = find_element_center(&click.url, &click.query) {
                if let Ok((x, y)) = get_chrome_origin() {
                    let viewport_top = get_absolute_viewport_top()?;
                    let abs_x = x as f64 + dx;
                    let abs_y = viewport_top as f64 + dy;

                    enigo.move_mouse(abs_x as i32, abs_y as i32, Abs).unwrap();
                    // Click twice - once to focus, once to click the button
                    enigo.button(Button::Left, Click).unwrap();
                    enigo.button(Button::Left, Click).unwrap();
                }
            }
        }
        thread::sleep(Duration::from_secs(3));
    }
}
