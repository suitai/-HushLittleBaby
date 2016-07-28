$(function() {

    set_lists();

    show_twtype("timeline");

    $("#search-text").val("");

    $("button.timeline").on('click', function() {
        show_twtype("timeline");
    });
    $("button.favorites").on('click', function() {
        show_twtype("favorites");
    });
    $("select.lists").change(function() {
        show_lists($("select.lists option:selected").val());
    });
    $("form[name='search']").submit(function(event) {
        event.preventDefault();
        show_search($(":text[name='search']").val());
    });
});

function show_twtype(twtype) {
    disable_button(true);
    show_tweets({
        twtype: twtype,
        params: {count: 100}
    });
    disable_button(false);
}

function show_lists(list_id) {
    disable_button(true);
    show_tweets({
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
    show_tweets({
        twtype: "search",
        params: {
            q: query,
            result_type: "recent",
            count: 100
        }
    });
    disable_button(false);
}

function disable_button(status) {
    $("#timeline-button").prop('disabled', status);
    $("#favorites-button").prop('disabled', status);
}

function show_tweets(data){
    console.log("show_tweets");
    console.log(data);
    $('.content').html("");

    get_tweets(data).done(function(result) {
        $('.content').html(result);
        console.log("get_tweets")
    }).fail(function(result) {
        $('.content').html("<p>" + result.statusText + "</p>");
        console.log("error");
        console.log(result);
    });
}

function set_lists(){
    get_lists().done(function(result) {
        $("select[name='lists']").append(result);
        console.log("get_lists")
    }).fail(function(result) {
        console.log(result);
    });
}

function get_tweets(data){
    return $.ajax({
        url: '_get_tweets',
        type: 'post',
        data: JSON.stringify(data),
        contentType: 'application/json',
        dataType: 'html',
    });
}

function get_lists(){
    return $.ajax({
        url: '_get_lists',
        type: 'get',
        dataType: 'html',
    });
}
