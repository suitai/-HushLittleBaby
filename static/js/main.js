$(function() {
    $("input[name='twtype']").change(function() {
        show_tweets({
            twtype: $(":input[name='twtype']:checked").val(),
            params: {count: 100}
        });
    });

        });
    });
});

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

function get_tweets(data){
    return $.ajax({
        url: '_get_tweets',
        type: 'post',
        data: JSON.stringify(data),
        contentType: 'application/json',
        dataType: 'html',
    });
}
