$(function() {

    write_lists();

    show_twtype("timeline");

    $("#search-text").val("");

    $("button.timeline").on('click', function() {
        show_twtype("timeline");
    });
    $("button.favorites").on('click', function() {
        show_twtype("favorites");
    });
    $("select.lists").change(function() {
        show_list($("select.lists option:selected").val());
    });
    $("form[name='search']").submit(function(event) {
        event.preventDefault();
        show_search($(":text[name='search']").val());
    });

    $(document).on('click', "span.retweet-count" , function() {
        if ($(this).attr("data-retweeted") == "False")  {
            if (change_tweet("retweet", $(this).attr("data-id"))) {
                $(this).attr("data-retweeted", "True");
                $(this).css('color', "#00cc00");
            }
        } else if ($(this).attr("data-retweeted") == "True")  {
            if (change_tweet("unretweet", $(this).attr("data-id"))) {
                $(this).attr("data-retweeted", "False");
                $(this).css('color', "#666666");
            }
        }
    });
    $(document).on('click', "span.favorite-count" , function() {
        if ($(this).attr("data-favorited") == "False")  {
            if (change_tweet("favorite-create", $(this).attr("data-id"))) {
                $(this).attr("data-favorited", "True");
                $(this).css('color', "#ff0000");
            }
        } else if ($(this).attr("data-favorited") == "True")  {
            if (change_tweet("favorite-destroy", $(this).attr("data-id"))) {
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
    disable_button(true);
    write_tweets({
        twtype: twtype,
        params: {count: 100}
    });
    disable_button(false);
}

function show_list(list_id) {
    disable_button(true);
    write_tweets({
        twtype: "list_status",
        params: {
            list_id: list_id,
            count: 100
        }
    });
    disable_button(false);
}

function show_search(query) {
    disable_button(true);
    write_tweets({
        twtype: "search",
        params: {
            q: query,
            result_type: "recent",
            count: 100
        }
    });
    disable_button(false);
}

function change_tweet(twtype, id) {
    var data = {
        twtype: twtype,
        params: {id: id}
    };
    console.log("change_tweets");
    console.log(data);
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

function disable_button(status) {
    $("#timeline-button").prop('disabled', status);
    $("#favorites-button").prop('disabled', status);
}

function write_tweets(data){
    console.log("show_tweets");
    console.log(data);
    $('.content').html("");

    get_tweets(data).done(function(result) {
        $('.content').html(result);
    }).fail(function(result) {
        $('.content').html("<p>" + result.statusText + "</p>");
        console.log("error");
        console.log(result);
    });
}

function write_lists(){
    get_lists().done(function(result) {
        $("select[name='lists']").append(result);
    }).fail(function(result) {
        console.log(result);
    });
}

function get_tweets(data){
    console.log("get_tweets")
    return $.ajax({
        url: '_get_tweets',
        type: 'post',
        data: JSON.stringify(data),
        contentType: 'application/json',
        dataType: 'html',
    });
}

function get_lists(){
    console.log("get_lists")
    return $.ajax({
        url: '_get_lists',
        type: 'get',
        dataType: 'html',
    });
}

function post_tweets(data){
    console.log("post_tweets")
    return $.ajax({
        url: '_post_tweets',
        type: 'post',
        data: JSON.stringify(data),
        contentType: 'application/json',
        dataType: 'text',
    });
}
