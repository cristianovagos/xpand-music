// Reproduzir o vídeo na modal
$(window).load(function(){
    playYouTubeVideo();

    function playYouTubeVideo() {
        var trigger = $("body").find('[data-toggle="modal"]');
        trigger.click(function () {
            var modal = $(this).data("target"),
                videoID = $(this).attr("data-videoID"),
                videoTitle = $(this).attr("data-videoTitle");
            $(modal + ' iframe').attr('src', videoID);
            $(modal + ' h4').text(videoTitle);
            $(modal + ' button.close').click(function () {
                $(modal + ' iframe').attr('src', videoID);
            });
        });
    }
});