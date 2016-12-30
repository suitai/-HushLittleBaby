
var prepend_tweets = function(data, result)
{
    var array = [];

    if (result['error']) {
        error_alert(result['error']);
        return;
    }
    $('div.tweet').each(function (i, elem) {
        array.push($(elem).attr('data-id-org'));
    });
    for (key in result) {
        if (($.inArray(result[key]['id_org'], array) == -1)) {
            $.tmpl(tweet_tmpl, result[key]).prependTo(data.dest);
            array.push(result[key]['id_org']);
        }
    }
    $('div.tweet-content').attr('data-twtype', data.twtype);
}

var append_tweets = function(data, result)
{
    var array = [];

    if (result['error']) {
        error_alert(result['error']);
        return;
    }
    $('div.tweet').each(function (i, elem) {
        array.push($(elem).attr('data-id-org'));
    });
    for (key in result) {
        if (($.inArray(result[key]['id_org'], array) == -1)) {
            $.tmpl(tweet_tmpl, result[key]).appendTo(data.dest);
            array.push(result[key]['id_org']);
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
    //var geo = get_geo();

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

    $.get("_get_tweet_template", function(data) {
        tweet_tmpl = data;
    }).done(function (result) {
        params = {count: 100};
        write_tweets({
            twtype: "home_timeline",
            params: params,
            dest: "div.tweets"
        }, append_tweets);
    });

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
        params = {list_id: $("select.lists option:selected").val(), count: 100};
        write_tweets({
            twtype: "list_status",
            params: params,
            dest: "div.tweets"
        }, append_tweets);
    });
    $("select.following").change(function() {
        $('div.tweet').remove();
        params = {user_id: $("select.following option:selected").val(), count: 100};
        write_tweets({
            twtype: "user_timeline",
            params: params,
            dest: "div.tweets"
        }, append_tweets);
    });
    $("form[name='search']").submit(function(event) {
        event.preventDefault();
        $('div.tweet').remove();
        params = {q: $(":text[name='search']").val(), count: 100};
        write_tweets({
            twtype: "search",
            params: params,
            dest: "div.tweets"
        }, append_tweets);
    });

    $(document).on('click', 'div.tweet-newer' , function() {
        var tmp_params = $.extend(true, {}, params);
        iconate($(this).children('.fa-caret-up').get(0), {
            from: 'fa-caret-up',
            to: 'fa-caret-up',
            animation: 'fadeOutTop'
        });
        tmp_params['since_id'] = $('div.tweet').eq(0).attr('data-id');
        write_tweets({
            twtype: $('div.tweet-content').attr('data-twtype'),
            params: tmp_params,
            dest: "div.tweets"
        }, prepend_tweets);
    });
    $(document).on('click', 'div.tweet-older' , function() {
        var tmp_params = $.extend(true, {}, params);
        iconate($(this).children('.fa-caret-down').get(0), {
            from: 'fa-caret-down',
            to: 'fa-caret-down',
            animation: 'fadeOutBottom'
        });
        tmp_params['max_id'] = $('div.tweet').eq(-1).attr('data-id');
        write_tweets({
            twtype: $('div.tweet-content').attr('data-twtype'),
            params: tmp_params,
            dest: "div.tweets"
        }, append_tweets);
    });

    $(document).on('click', 'span.retweet-count' , function() {
        var tweet_id = $(this).parents('.tweet').attr('data-id');
        if ($(this).attr('data-retweeted') == 'false') {
            var ret = request_post({twtype: 'retweet', params: {id: tweet_id}});
            if (ret) {
                iconate($(this).children('.fa-refresh').get(0), {
                    from: 'fa-refresh',
                    to: 'fa-refresh',
                    animation: 'rubberBand'
                });
                var num = Number($(this).children('.retweet-num').html());
                $(this).children('.retweet-num').html(num + 1);
                $(this).attr('data-retweeted', 'true');
                $(this).css('color', '#00cc00');
            }
        } else if ($(this).attr('data-retweeted') == 'true') {
            var ret = request_post({twtype: 'unretweet', params: {id: tweet_id}});
            if (ret) {
                var num = Number($(this).children('.retweet-num').html());
                $(this).children('i.retweet-num').html(num - 1);
                $(this).attr('data-retweeted', 'false');
                $(this).css('color', '#666666');
            }
        }
    });
    $(document).on('click', 'span.favorite-count' , function() {
        var tweet_id = $(this).parents('.tweet').attr('data-id');
        if ($(this).attr('data-favorited') == 'false') {
            var ret = request_post({twtype: 'favorite-create', params: {id: tweet_id}});
            if (ret) {
                iconate($(this).children('.fa-heart').get(0), {
                    from: 'fa-heart',
                    to: 'fa-heart',
                    animation: 'rubberBand'
                });
                var num = Number($(this).children('.favorite-num').html());
                $(this).children('i.favorite-num').html(num + 1);
                $(this).attr('data-favorited', 'true');
                $(this).css('color', '#ff0000');
            }
        } else if ($(this).attr('data-favorited') == 'true')  {
            var ret = request_post({twtype: 'favorite-destroy', params: {id: tweet_id}});
            if (ret) {
                var num = Number($(this).children('.favorite-num').html());
                $(this).children('i.favorite-num').html(num - 1);
                $(this).attr('data-favorited', 'false');
                $(this).css('color', '#666666');
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

function loading_image(status)
{
    var height = $('div.tweet-content').height();
    $('div.fade').css("height", height);

    if (status == true) {
        $("div.loader").fadeIn(200);
        $("div.fade").fadeIn(200);
    } else {
        $("div.fade").delay(300).fadeOut(200);
        $("div.loader").delay(300).fadeOut(200);
    }
}

function disable_button(status)
{
    $("button.timeline").prop('disabled', status);
    $("button.favorites").prop('disabled', status);
    $("select.lists").prop('disabled', status);
    $("select.following").prop('disabled', status);
    $("form.search-form").prop('disabled', status);
    if (status == true) {
        $("div.tweet-newer").css('pointer-events', "none");
        $("div.tweet-older").css('pointer-events', "none");
    } else {
        $("div.tweet-newer").css('pointer-events', "auto");
        $("div.tweet-older").css('pointer-events', "auto");
    }
    loading_image(status);
}

function get_geo()
{
    $.get("_get_ipaddr", function (data) {
        get_tweets_js({twtype: "geosearch", params: {ip: data}}).done(function (result) {
            console.log(result);
            return result;
        }).fail(function(result) {
            error_confirm(result);
        });
    });
}

function write_oath2_tweets(data, func)
{
    disable_button(true);
    get_oath2_tweets_js(data).done(function (result) {
        func(data, result);
        disable_button(false);
    }).fail(function(result) {
        error_confirm(result);
        disable_button(false);
    });
}

function write_tweets(data, func)
{
    disable_button(true);
    get_tweets_js(data).done(function (result) {
        func(data, result);
        disable_button(false);
    }).fail(function(result) {
        error_confirm(result);
        disable_button(false);
    });
}

function get_oath2_tweets_js(data)
{
    return $.ajax({
        url: '_get_oath2_tweets_js',
        type: 'post',
        data: JSON.stringify(data),
        contentType: 'application/json',
        dataType: 'json',
    });
}

function get_tweets_js(data)
{
    return $.ajax({
        url: '_get_tweets_js',
        type: 'post',
        data: JSON.stringify(data),
        contentType: 'application/json',
        dataType: 'json',
    });
}

function get_tweets(data)
{
    return $.ajax({
        url: '_get_tweets',
        type: 'post',
        data: JSON.stringify(data),
        contentType: 'application/json',
        dataType: 'html',
    });
}

function request_post(data)
{
    return post_tweets(data).done(function(result) {
        if (result == "success") {
            return true;
        } else {
            error_alert(result);
            return false;
        }
    }).fail(function(result) {
        error_confirm(result);
    });
}

function post_tweets(data)
{
    return $.ajax({
        url: '_post_tweets',
        type: 'post',
        data: JSON.stringify(data),
        contentType: 'application/json',
        dataType: 'text',
    });
}

function error_alert(result)
{
    console.log(result);
    alert(result);
}

function error_confirm(result)
{
    console.log(result);
    if (!confirm("エラーが発生しました。ログアウトします\n" + result)){
        return;
    } else {
        location.href = "/logout";
    }
}
