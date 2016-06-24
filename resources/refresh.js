var refreshFolder = function () {
    $.post('/refreshfolder',
    {
        null : null
    },
    function(data) {
        if(data["msg"]) $("pre").html(data["msg"]);
        else alert("There are no new files.");
    },
    'json'
    );
};


$(document).ready(function() {
        $("#button_refresh").click(refreshFolder);
});
