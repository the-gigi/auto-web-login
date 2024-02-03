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

    window.addEventListener('load', function() {
        console.log('auto-aws-sso-login is here!');
        var buttonIds = ['cli_verification_btn', 'cli_login_button'];
        buttonIds.forEach(function(buttonId) {
            var button = document.getElementById(buttonId);
            if (button) {
                button.click();
            }
        });
    });
})();