$(function() {

    write_lists();
    show_tweets("home_timeline", {}, "overwrite");
    $("#search-text").val("");

    $("button.timeline").on('click', function() {
        show_tweets("home_timeline", {}, "overwrite");
    });
    $("button.favorites").on('click', function() {
        show_tweets("favorites", {}, "overwrite");
    });
    $("select.lists").change(function() {
        show_tweets(
            "list_status",
            {list_id: $("select.lists option:selected").val()},
            "overwrite"
        );
    });
    $("form[name='search']").submit(function(event) {
        event.preventDefault();
        show_tweets(
            "search",
            { q: $(":text[name='search']").val()},
            "overwrite"
        );
    });

    $(document).on('click', "div.tweet-newer" , function() {
        update_tweets(
            $('div.tweet-content').attr('data-twtype'),
            {since_id: $(this).attr('data-max_id')},
            "prepend"
        );
    });
    $(document).on('click', "div.tweet-older" , function() {
        update_tweets(
            $('div.tweet-content').attr('data-twtype'),
            {max_id: $(this).attr('data-since_id')},
            "append"
        );
    });

    $(document).on('click', "span.retweet-count" , function() {
        var tweet_id = $(this).parent().parent().attr('data-id');
        if ($(this).attr("data-retweeted") == "False")  {
            if (change_status("retweet", tweet_id)) {
                $(this).attr("data-retweeted", "True");
                $(this).css('color', "#00cc00");
            }
        } else if ($(this).attr("data-retweeted") == "True")  {
            if (change_status("unretweet", tweet_id)) {
                $(this).attr("data-retweeted", "False");
                $(this).css('color', "#666666");
            }
        }
    });
    $(document).on('click', "span.favorite-count" , function() {
        var tweet_id = $(this).parent().parent().attr('data-id');
        if ($(this).attr("data-favorited") == "False")  {
            if (change_status("favorite-create", tweet_id)) {
                $(this).attr("data-favorited", "True");
                $(this).css('color', "#ff0000");
            }
        } else if ($(this).attr("data-favorited") == "True")  {
            if (change_status("favorite-destroy", tweet_id)) {
                $(this).attr("data-favorited", "False");
                $(this).css('color', "#666666");
            }
        }
    });

    $(document).on('mouseover',"span.retweet-count", function() {
        if ($(this).attr("data-retweeted") == "False")  {
            $(this).css('color', "#00cc00");
        }
    });
    $(document).on('mouseout',"span.retweet-count", function() {
        if ($(this).attr("data-retweeted") == "False")  {
            $(this).css('color', "#666666");
        }
    });
    $(document).on('mouseover',"span.favorite-count", function() {
        if ($(this).attr("data-favorited") == "False")  {
            $(this).css('color', "#ff0000");
        }
    });
    $(document).on('mouseout',"span.favorite-count" ,function() {
        if ($(this).attr("data-favorited") == "False")  {
            $(this).css('color', "#666666");
        }
    });
    $(document).on('mouseover',"div.tweet-newer", function() {
        $(this).css('background-color', "#f0f0f0");
    });
    $(document).on('mouseout',"div.tweet-newer" ,function() {
        $(this).css('background-color', "#ffffff");
    });
    $(document).on('mouseover',"div.tweet-older", function() {
        $(this).css('background-color', "#f0f0f0");
    });
    $(document).on('mouseout',"div.tweet-older" ,function() {
        $(this).css('background-color', "#ffffff");
    });
});

function update_tweets(twtype, params, mode) {
    if (twtype == "search") {
        params['q'] = $('div.tweet-content').attr('data-q');
    } else if (twtype == "list_status") {
        params['list_id'] = $('div.tweet-content').attr('data-list_id');
    }
    show_tweets(twtype, params, mode);
}

function show_tweets(twtype, params, mode) {
    params['count'] = 100;
    write_tweets({
        twtype: twtype,
        params: params,
        mode: mode
    });
}

function change_status(twtype, id) {
    return request_post({
        twtype: twtype,
        params: {id: id}
    });
}

function disable_button(status) {
    $("button.timeline").prop('disabled', status);
    $("button.favorites").prop('disabled', status);
    $("select.lists").prop('disabled', status);
    $("form.search-form").prop('disabled', status);
}

function request_post(data) {
    return post_tweets(data).done(function(result) {
        console.log(result);
        if (result == "success") {
            return true;
        } else {
            return false;
        }
    }).fail(function(result) {
        console.log("error");
        console.log(result);
        alert(result.statusTexte);
        location.href = "/logout"
    });
}

function write_tweets(data) {
    disable_button(true);
    get_tweets(data).done(function(result) {
        var html = $.parseHTML(result);
        var error = $(html).find('.error');

        if (error.length > 0) {
            alert($(error).find("p").text());
            return;
        }

        switch (data['mode']) {
            case "overwrite":
                $('.content').html("");
                $('#lightbox').remove();
                $('#lightboxOverlay').remove();
                $('.content').html(result);
                break;

            case "prepend":
                var tweet = $(html).find('.tweet');
                var newer = $(html).find('.tweet-newer');
                var max_id = $('.tweet-newer').attr('data-max_id');
                $('.tweet[data-id='+max_id+']:first').remove();
                $('.tweet-newer').remove();
                $('.tweets').prepend($(tweet));
                $('.tweet-content').prepend(older);
                break;

            case "append":
                var tweet = $(html).find('.tweet');
                var older = $(html).find('.tweet-older');
                var since_id = $('.tweet-older').attr('data-since_id');
                $('.tweet[data-id='+since_id+']:first').remove();
                $('.tweet-older').remove();
                $('.tweets').append($(tweet));
                $('.tweet-content').append(older);
                break;
        }
    }).fail(function(result) {
        console.log("error");
        console.log(result);
        alert(result.statusTexte);
        location.href = "/logout"
    });
    disable_button(false);
}

function write_lists(){
    data = {
        twtype: "lists",
        params: {}
    }
    get_tweets(data).done(function(result) {
        $("select[name='lists']").append(result);
    }).fail(function(result) {
        console.log("error");
        console.log(result);
        alert(result.statusTexte);
        location.href = "/logout"
    });
}

function get_tweets(data){
    console.log("get_tweets")
    console.log(data);
    return $.ajax({
        url: '_get_tweets',
        type: 'post',
        data: JSON.stringify(data),
        contentType: 'application/json',
        dataType: 'html',
    });
}

function post_tweets(data){
    console.log("post_tweets")
    console.log(data);
    return $.ajax({
        url: '_post_tweets',
        type: 'post',
        data: JSON.stringify(data),
        contentType: 'application/json',
        dataType: 'text',
    });
}
