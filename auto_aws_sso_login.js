// ==UserScript==
// @name         auto-aws-sso-login
// @namespace    http://tampermonkey.net/
// @version      2024-02-02
// @description  Automatically click the buttons when doing aws sso login
// @author       the.gigi@gmail.com
// @include      https://device.sso.*.amazonaws.com/*
// @include      https://d-*.awsapps.com/start/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    var attempt = 0;
    var maxAttempts = 5; // Maximum number of attempts to find and click the button

    function tryClickButton() {
        attempt++;
        if (attempt > maxAttempts) {
            console.log('Max attempts reached. Stopping.');
            return;
        }

        console.log('Attempt:', attempt);
        var buttonFound = false;
        var buttonIds = ['cli_verification_btn', 'cli_login_button'];
        buttonIds.forEach(function(buttonId) {
            var button = document.getElementById(buttonId);
            if (button) {
                button.click();
                buttonFound = true;
            }
        });

        if (!buttonFound) {
            console.log('No button found, trying again in 1 second...');
            setTimeout(tryClickButton, 1000); // Wait for 1 second before trying again
        }
    }

    window.addEventListener('load', tryClickButton);
})();
