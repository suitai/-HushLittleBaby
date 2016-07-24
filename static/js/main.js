$(function() {
    $("input[name='twtype']").change(function() {
        $('.content').html("");
        var data = {twtype: $("input[name='twtype']:checked").val()};
        $.ajax({
            url: '/_get_tweets',
            type: 'get',
            data: data,
            dataType: 'html',
        }).done(function(result) {
            $('.content').html(result);
        }).fail(function(result) {
            $('.content').html(result);
            console.log("ERROR: ");
        });
    });
});
