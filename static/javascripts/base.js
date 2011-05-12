$(document).ready(function() {
    // random code from the internet to get csrf validation to work on ajax
    $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                    // Only send the token to relative URLs i.e. locally.
                    xhr.setRequestHeader("X-CSRFToken",
                        $("#csrfmiddlewaretoken").val());
                }
            }
    });
    // POST request
    $('html').ajaxSend(function(event, xhr, settings) {
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
        function sameOrigin(url) {
            // url could be relative or scheme relative or absolute
            var host = document.location.host; // host + port
            var protocol = document.location.protocol;
            var sr_origin = '//' + host;
            var origin = protocol + sr_origin;
            // Allow absolute or scheme relative URLs to same origin
            return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
        }
        function safeMethod(method) {
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    });

    // search results pop under search bar
    $('#search-bar').keyup(function(e) {
        var code = (e.which ? e.which : e.keyCode);
        if (code != '40' && code != '38')
            sendValue($(this).val());
    });

    // handle key presses to scroll through options
    $('#search-bar').keydown(function(e) {
        var code = (e.which ? e.which : e.keyCode);
        if (code == '40') {
            handleSearchKeyDown(true, false, false);
            return false; // return false overrides default action
        }
        else if (code == '38') {
            handleSearchKeyDown(false, true, false);
            return false;
        }
        else if (code == '13') {
            if (handleSearchKeyDown(false, false, true))
                return false;
        }
        else {
            handleSearchKeyDown(false, false, false);
        }
    });
});
