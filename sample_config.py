# The buttons on these pages need to be clicked (keys must use wildcards only)
url_buttons_dict = {
    "https://device.sso.*.amazonaws.com/*": ["document.getElementById('cli_verification_btn')"],
    "https://d-*.awsapps.com/start/*": ["document.getElementById('cli_login_button')"],
}

# These buttons must be clicked by simulated user
user_click_dict = {
    "https://<your company>.onelogin.com/login2/":
        """Array.from(document.querySelectorAll('span'))
            .some(span => span.textContent.includes('Change Authentication Factor')) 
                ? null 
                : document.querySelector('button[type="submit"]')"""
}

# These tabs should be closed: key is a substring of url. value is a query that returns an element.
url_query_dict = {
    "https://<your company>.onelogin.com/login2/": "document.querySelector('button[type=\"submit\"]')"
}
