// ==UserScript==
// @name         auto-web-login
// @namespace    http://tampermonkey.net/
// @version      2024-03-31
// @description  Automatically click the buttons when doing aws sso login
// @author       the.gigi@gmail.com
// @grant        none
// @include      https://device.sso.*.amazonaws.com/*
// @include      https://d-*.awsapps.com/start/*
// ==/UserScript==

(function() {
    'use strict';

    var maxAttempts = 5;
    var attempt = 0;

    function tryClickButtons() {
        if (attempt >= maxAttempts) {
            console.log("Max attempts reached. Stopping.");
            return;
        }
        attempt++;
        console.log("Attempt:", attempt);

        var urlButtonMappings = {
            "https://device.sso..*.amazonaws.com/.*": [
                        "cli_verification_btn"
            ],
            "https://d-.*.awsapps.com/start/.*": [
                        "cli_login_button"
            ]
        };
        var currentUrl = window.location.href;

        var buttonClicked = false;
        Object.keys(urlButtonMappings).forEach(function(pattern) {
            var regex = new RegExp(pattern);
            if (regex.test(currentUrl)) {
                var buttonIds = urlButtonMappings[pattern];
                buttonIds.forEach(function(buttonId) {
                    console.log('Trying button id: ' + buttonId);
                    var button = document.getElementById(buttonId);
                    if (button) {
                        console.log('Found and clicked button id: ' + buttonId);
                        button.click();
                        buttonClicked = true;
                    }
                });
            }
        });

        if (!buttonClicked) {
            console.log("No button found, trying again in 1 second...");
            setTimeout(tryClickButtons, 1000); // Wait for 1 second before trying again
        }
    }

    window.addEventListener('load', tryClickButtons);
})();