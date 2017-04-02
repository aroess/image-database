var imgResize = function () {
    var w = $("IMG[name=imageEdit]").attr("width"),
        h = $("IMG[name=imageEdit]").attr("height"),
        w_max = $(window).width() - 100,
        h_max = $(window).height() - 150;

    // width too large?
    if (w > w_max) {
        $("IMG[name=imageEdit]").attr("width", w_max);
        $("IMG[name=imageEdit]").attr("height", Math.floor(h * (w_max / w)));
        w = $("IMG[name=imageEdit]").attr("width");
        h = $("IMG[name=imageEdit]").attr("height");
    }

    // height too large?
    if (h > h_max) {
        $("IMG[name=imageEdit]").attr("height", h_max);
        $("IMG[name=imageEdit]").attr("width", Math.floor(w * (h_max / h)));
    }
};


var addKey = function () {
    var fileID = $("IMG[name=imageEdit]").attr("id"); 
    var keyword = $("input[name=keyword]").val();
    if (confirm("Add keyword '" + keyword + "' to image?")) {
    $.post('/addtagtoimage',
           {
               "fileID" : fileID,
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

var deleteTag = function (filename) {
    if (confirm("Remove tag '" + filename + "' from image?")) {
        var fileID = $("IMG[name=imageEdit]").attr("id");
        $.post('/deletetagfromimage',
               {
                   "fileID" : fileID,
                   "tag"    : filename
               },
               function(data) {
                   window.location.reload();
               },
               'json'
              );
    }
}

var deleteImage = function () {
    var fileID = $("IMG[name=imageEdit]").attr("id");
    if (confirm("Are you sure? This action will delete the database\nentry AND the file on the disk.")) {
    $.post('/deleteimage',
           {
               "fileID" : fileID,
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
        deleteTag(this.name);
    });
});
