$(function() {

    write_lists();
    show_tweets("timeline", {}, "overwrite");
    $("#search-text").val("");

    $("button.timeline").on('click', function() {
        show_tweets("timeline", {}, "overwrite");
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
    });

    $(document).on('click', "span.retweet-count" , function() {
        var tweet_id = $(this).parent().parent().attr('id');
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
        var tweet_id = $(this).parent().parent().attr('id');
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
});

function show_twtype(twtype) {
    write_tweets({
        twtype: twtype,
        params: {count: 100}
    });
}

function show_list(list_id) {
    write_tweets({
        twtype: "list_status",
        params: {
            list_id: list_id,
            count: 100
        }
    });
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
    $("#timeline-button").prop('disabled', status);
    $("#favorites-button").prop('disabled', status);
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
        return false;
    });
}

function write_tweets(data) {
    disable_button(true);
    if (data['mode'] == "overwrite") {
        $('.content').html("");
    }
    get_tweets(data).done(function(result) {
        switch (data['mode']) {
            case "overwrite":
                $('.content').html(result);
                break;
        }
    }).fail(function(result) {
        $('.content').html("<p>" + result.statusText + "</p>");
        console.log("error");
        console.log(result);
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
        console.log(result);
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
