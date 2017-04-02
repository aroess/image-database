var currPage = 0; 
var htmlOut = ""; 

String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number){ 
        return typeof (args[number] != 'undefined') ? args[number] : match;
    });
}

var splitext = function(path) {
    var base = path.toString().split('.');
    var ext  = base.pop();
    return [base.join('.'), ext];
};

var showResults = function(data) {
    htmlOut = "";
    if(data["result"].length == 0) {
        if(currPage==0){ // no data on first page
            htmlOut = '<p>no results...</p>';
            $('#footer').hide();            
        } 
        else {            // no data on page > 0
            htmlOut += '<p><br>no more results... <a href="#top">top</a></p>';
            $('#footer').hide();
        }  
    } 
    else {
        htmlOut += '<h6><span class="label label-default">Page {0}</span></h6>'.format(currPage+1);
        for(var i=0; i<data["result"].length; i++) {
            htmlOut +=
            '<div class="pictureDiv"><a href="{0}" id="{2}">\
            <img src="static/thumbs/{1}" width="100" height="100" />\
</a></div>'.format(data["result"][i][0], data["result"][i][1], data["result"][i][2]);
        }
        $('#footer').show();
        currPage++;          
    }
    $('#searchResults').append(htmlOut);
    $("html,body").animate({ scrollTop: $(document).height() }, 'slow');
};  

var addKey = function() {
    $('.typeahead').typeahead('close');
    if(!$("input[name=searchTag]").val()) return;
    currPage=0; $('#searchResults').html('');
    var keyword = $("input[name=searchTag]").val();
    $("#tagBar").append(
    "<input type=button class='btn btn-primary btn-sm tagBarButton' " +
        "value='{0}' name='{1}'/> ".format(keyword + " ✖", keyword)
    );

    $("input[name=searchTag]").val("")
    getJsonData(); 
};

// JSON request
var getJsonData = function() {
        var winTileWidth = Math.floor(($(window).width()-200)/105);
        var winTileHeight =  Math.floor(($(window).height()-200)/105);
        var taglist = [];

        $("#tagBar>.tagBarButton").each(function() {
            taglist.push(this.name);
        });
        
        $.post('/search',
            { 
                "searchKey" : taglist.join(','),
                "pageCount" : currPage,
                "offset" : winTileWidth * winTileHeight
            },
            function(data){
                showResults(data);
            }, 
            'json'
        );       
}

$(document).ready(function() { 
    // Form handling
    $("#tagBar").delegate(".tagBarButton", "click", function() {
        this.remove();
        $('#searchResults').html("");
        htmlOut = "";
        currPage = 0;
        getJsonData();
    });
   
    $("input[name=next]").click(function() {
        getJsonData(); 
    });   

    $("#button_go").click(addKey);    

    // get random image selection
    getJsonData(); 

    // init typeahead
    $.get('../static/tags.json', function(data){
        $(".typeahead").typeahead({ 
            source:data,
            afterSelect: addKey
        });
    },'json');

    // image hover code
    // show image container when thumb is clicked
    $("body").on("click", ".pictureDiv", function(event) {
        event.preventDefault();
        var imgUrl = $(this).find(">:first-child").attr("href");
        var imgID  = $(this).find(">:first-child").attr("id");
        var htmlOut = "<a href='static/{0}'><img class='menu' src='static/resources/expand.png'></a><br>".format(imgUrl);
        htmlOut    += "<a href='edit/{0}'><img class='menu' src='static/resources/edit.png'></a>".format(imgID);
        htmlOut    += "<img id='main' src='static/{0}'>".format(imgUrl);
        $("#imgHover").html(htmlOut);
        $("#imgHover").fadeIn(300);
    });

    // hide image container if enlarged image is clicked
    $(document).on("click", "#imgHover img", function () {
        $("#imgHover").fadeOut(300);
    });

});
