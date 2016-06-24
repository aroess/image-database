var imgResize = function () {
    var w = $("#imageEdit").attr("width"),
        h = $("#imageEdit").attr("height"),
        w_max = $(window).width() - 100,
        h_max = $(window).height() - 150;

    // width too large?
    if (w > w_max) {
        $("#imageEdit").attr("width", w_max);
        $("#imageEdit").attr("height", Math.floor(h * (w_max / w)));
        w = $("#imageEdit").attr("width");
        h = $("#imageEdit").attr("height");
    }

    // height too large?
    if (h > h_max) {
        $("#imageEdit").attr("height", h_max);
        $("#imageEdit").attr("width", Math.floor(w * (h_max / h)));
    }
};


var addKey = function () {
    var filename = $("#imageEdit").attr("src").split("/");
    filename = filename[filename.length-1];
    var keyword = $("input[name=keyword]").val();
    if (confirm("Add keyword '" + keyword + "' to image?")) {
    $.post('/addtagtoimage',
    {
        "filename" : filename,
        "keywords" : keyword
    },
    function(data) {
        if(data["msg"]) alert(data["msg"]);
        else window.location.reload();
    },
    'json'
    );
    }
};

var deleteImage = function () {
    var filename = $("#imageEdit").attr("src").split("/");
    filename = filename[filename.length-1];
    if (confirm("Are you sure? This action will delete the database\nentry AND the file on the disk.")) {
    $.post('/deleteimage',
    {
        "filename" : filename,
    },
    function(data) {
        if(data["msg"]) {
            alert(data["msg"]);
            if (data["msg"] == "Image successfully deleted!") window.location = "/";
        }
    },
    'json'
    );
    }
};

$(document).ready(function() {

    imgResize();

    $("input[name=keyword]").keyup(function(event) {
    if(event.keyCode == 13) addKey();
    });

    $("#button_add").click(addKey);
    $("#button_delete").click(deleteImage);

    // init typeahead
    $.get('../static/tags.json', function(data){
        $(".typeahead").typeahead({
            source:data,
            afterSelect: addKey
        });
    },'json');


    // "delete tag"-button handler
    $("#tagbuttons input").click(function() {
    if (confirm("Remove tag '" + this.name + "' from image?")) {
        var filename = $("#imageEdit").attr("src").split("/");
        filename = filename[filename.length-1];
        $.post('/deletetagfromimage',
        {
            "filename" : filename,
            "tag" :      this.name
        },
        function(data) {
            window.location.reload();
        },
        'json'
        );
    }
    });
});
