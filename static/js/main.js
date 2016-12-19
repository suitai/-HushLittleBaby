
var prepend_tweets = function(data, result)
{
    var array = [];

    if (result["error"]) {
        alert(result['error'][0]);
        return;
    }
    $('div.tweet').each(function (i, elem) {
        array.push(Number($(elem).attr('data-id')));
    });
    for (key in result) {
        if (($.inArray(result[key]['id'], array) == -1)) {
            $.tmpl(tweet_tmpl, result[key]).prependTo(data.dest);
        }
    }
    $('div.tweet-content').attr('data-twtype', data.twtype)
}

var append_tweets = function(data, result)
{
    var array = [];

    if (result["error"]) {
        alert(result['error'][0]);
        return;
    }
    $('div.tweet').each(function (i, elem) {
        array.push(Number($(elem).attr('data-id')));
    });
    for (key in result) {
        if (($.inArray(result[key]['id'], array) == -1)) {
            $.tmpl(tweet_tmpl, result[key]).appendTo(data.dest);
        }
    }
    $('div.tweet-content').attr('data-twtype', data.twtype)
}

var append_lists = function(data, result)
{
    for (key in result) {
        $.tmpl('<option value="${id}">${name}</option>', result[key]).appendTo(data.dest);
    }
}

$(function()
{
    $.get("_get_ipaddr", function(data) { ipaddr = data; console.log(ipaddr);});
    $.get("_get_tweet_template", function(data) { tweet_tmpl = data; });
    $.get("_get_tweets_head", function(data) { $('.content').prepend(data); });

    write_tweets({
        twtype: "lists",
        params: {},
        dest: "select[name='lists']"
    }, append_lists);

    write_tweets({
        twtype: "friends",
        params: {count: 200},
        dest: "select[name='following']"
    }, append_lists);

    params = {count: 100};
    write_tweets({
        twtype: "home_timeline",
        params: params,
        dest: "div.tweets"
    }, append_tweets);

    $("button.timeline").on('click', function() {
        $('div.tweet').remove();
        params = {count: 100};
        write_tweets({
            twtype: "home_timeline",
            params: params,
            dest: "div.tweets"
        }, append_tweets);
    });
    $("button.favorites").on('click', function() {
        $('div.tweet').remove();
        params = {count: 100};
        write_tweets({
            twtype: "favorites",
            params: params,
            dest: "div.tweets"
        }, append_tweets);
    });
    $("select.lists").change(function() {
        $('div.tweet').remove();
        params = {list_id: $("select.lists option:selected").val(),
                  count: 100};
        write_tweets({
            twtype: "list_status",
            params: params,
            dest: "div.tweets"
        }, append_tweets);
    });
    $("select.following").change(function() {
        $('div.tweet').remove();
        params = {user_id: $("select.following option:selected").val(),
                  count: 100};
        write_tweets({
            twtype: "user_timeline",
            params: params,
            dest: "div.tweets"
        }, append_tweets);
    });
    $("form[name='search']").submit(function(event) {
        event.preventDefault();
        $('div.tweet').remove();
        params = {q: $(":text[name='search']").val()};
        write_tweets({
            twtype: "search",
            params: params,
            dest: "div.tweets"
        }, append_tweets);
    });

    $(document).on('click', "div.tweet-newer" , function() {
        var tmp_params = params;
        tmp_params['since_id'] = $('div.tweet').eq(0).attr('data-id');

        write_tweets({
            twtype: $('div.tweet-content').attr('data-twtype'),
            params: tmp_params,
            dest: "div.tweets"
        }, prepend_tweets);
    });
    $(document).on('click', "div.tweet-older" , function() {
        var tmp_params = params;
        tmp_params['max_id'] = $('div.tweet').eq(-1).attr('data-id');
        write_tweets_js({
            twtype: $('div.tweet-content').attr('data-twtype'),
            params: tmp_params,
            dest: "div.tweets"
        }, append_tweets);
    });

    $(document).on('click', "span.retweet-count" , function() {
        var tweet_id = $(this).parent().parent().attr('data-id');
        if ($(this).attr("data-retweeted") == "false") {
            var ret = request_post({twtype: "retweet", params: {id: tweet_id}});
            if (ret) {
                $(this).attr("data-retweeted", "true");
                $(this).css('color', "#00cc00");
            }
        } else if ($(this).attr("data-retweeted") == "true") {
            var ret = request_post({twtype: "unretweet", params: {id: tweet_id}});
            if (ret) {
                $(this).attr("data-retweeted", "false");
                $(this).css('color', "#666666");
            }
        }
    });
    $(document).on('click', "span.favorite-count" , function() {
        var tweet_id = $(this).parent().parent().attr('data-id');
        if ($(this).attr("data-favorited") == "false") {
            var ret = request_post({twtype: "favorite-create", params: {id: tweet_id}});
            if (ret) {
                $(this).attr("data-favorited", "true");
                $(this).css('color', "#ff0000");
            }
        } else if ($(this).attr("data-favorited") == "true")  {
            var ret = request_post({twtype: "favorite-destroy", params: {id: tweet_id}});
            if (ret) {
                $(this).attr("data-favorited", "false");
                $(this).css('color', "#666666");
            }
        }
    });

    $(document).on('mouseover',"span.retweet-count", function() {
        if ($(this).attr("data-retweeted") == "false")  {
            $(this).css('color', "#00cc00");
        }
    });
    $(document).on('mouseout',"span.retweet-count", function() {
        if ($(this).attr("data-retweeted") == "false")  {
            $(this).css('color', "#666666");
        }
    });
    $(document).on('mouseover',"span.favorite-count", function() {
        if ($(this).attr("data-favorited") == "false")  {
            $(this).css('color', "#ff0000");
        }
    });
    $(document).on('mouseout',"span.favorite-count" ,function() {
        if ($(this).attr("data-favorited") == "false")  {
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

function disable_button(status) {
    $("button.timeline").prop('disabled', status);
    $("button.favorites").prop('disabled', status);
    $("select.lists").prop('disabled', status);
    $("form.search-form").prop('disabled', status);
}

function write_tweets(data, func)
{
    disable_button(true);
    get_tweets_js(data).done(function (result) {
        func(data, result);
    }).fail(function(result) {
        console.log("error");
        console.log(result);
        alert(result.statusTexte);
        location.href = "/logout"
    });
    disable_button(false);
}

function get_tweets_js(data){
    console.log(data);
    return $.ajax({
        url: '_get_tweets_js',
        type: 'post',
        data: JSON.stringify(data),
        contentType: 'application/json',
        dataType: 'json',
    });
}

function get_tweets(data){
    console.log("get_tweets");
    console.log(data);
    return $.ajax({
        url: '_get_tweets',
        type: 'post',
        data: JSON.stringify(data),
        contentType: 'application/json',
        dataType: 'html',
    });
}

function request_post(data) {
    return post_tweets(data).done(function(result) {
        if (result == "success") {
            return true;
        } else {
            console.log("error");
            console.log(result);
            alert(result);
            return false;
        }
    }).fail(function(result) {
        console.log("error");
        console.log(result);
        alert(result.statusTexte);
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
