# The buttons on these pages need to be clicked (keys must use wildcards only)
url_buttons_dict = {
    "https://device.sso.*.amazonaws.com/*": [
        "document.getElementById('cli_verification_btn')"],
    "https://d-*.awsapps.com/start/*": [
        "document.getElementById('cli_login_button')",
        "document.querySelector('button[data-testid=\"allow-access-button\"]')"
    ],
}

# These tabs should be closed: key is a regex of the URL. value is a query that returns an element.
url_query_dict = {
    "https://d-[a-zA-Z0-9-]*.awsapps.com/start/.*":
        "Array.from(document.querySelectorAll('div')).find(el => el.textContent === 'Request approved');"
}
