// ==UserScript==
// @name         auto-web-login
// @namespace    http://tampermonkey.net/
// @version      2024-04-25
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

    function handleButton(button) {
        if (!button) {
            return false;
        }
        console.log('Found and clicked button');
        button.click();
        return true;
    }

    function tryClickButtons() {
        if (attempt >= maxAttempts) {
            console.log("Max attempts reached. Stopping.");
            return;
        }
        attempt++;
        console.log("Attempt:", attempt);
        var currentUrl = window.location.href;
        var buttonClicked = false;
        var regex = null;
        var button = null;

        regex = new RegExp("https://device.sso..*.amazonaws.com/.*");
        if (regex.test(currentUrl)) {
            button = document.getElementById('cli_verification_btn');
            if (handleButton(button)) {
                return;
            }
        }

        regex = new RegExp("https://d-.*.awsapps.com/start/.*");
        if (regex.test(currentUrl)) {
            button = document.getElementById('cli_login_button');
            if (handleButton(button)) {
                return;
            }
            button = document.querySelector('button[data-testid="allow-access-button"]');
            if (handleButton(button)) {
                return;
            }
        }

        console.log("No button found, trying again in 1 second...");
        setTimeout(tryClickButtons, 1000); // Wait for 1 second before trying again
    }

    window.addEventListener('load', tryClickButtons);
})();
