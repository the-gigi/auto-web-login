# The buttons on these pages need to be clicked (keys must use wildcards only)
url_buttons_dict = {
    "https://device.sso.*.amazonaws.com/*": ["cli_verification_btn"],
    "https://d-*.awsapps.com/start/*": ["cli_login_button"]
}

# These tabs should be closed: key is a substring of url. value is a query that returns an element.
url_query_dict = {
    "awsapps.com/start/": "Array.from(document.querySelectorAll('div')).find(el => el.textContent === 'Request approved');"
}
