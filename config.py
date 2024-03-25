# The buttons on these pages need to be clicked
url_buttons_dict = {
    "https://device.sso.*.amazonaws.com/*": "cli_verification_btn",
    "https://d-*.awsapps.com/start/*": "cli_login_button"
}

# These tabs should be closed: url should match pattern and query should return an element
url_query_dict = {
    "awsapps.com/start/": "Array.from(document.querySelectorAll('div')).find(el => el.textContent === 'Request approved');"
}
