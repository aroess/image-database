var addKey = function () { 
     var keyword = $("input[name=keyword]").val();
     if (confirm("Add keyword '" + keyword + "' to database?")) {
     $.post('/addtagtodb',
        { 
        "newkey" : keyword
        },
        function(data) {
        if(data["msg"]) alert(data["msg"]);
        else window.location.reload();
        },
        'json'
    ); 
    }
};

$(document).ready(function(){
    $("input[name=keyword]").keyup(function(event) {
    if(event.keyCode == 13) addKey();
    });

    $("#basic-addon1").click(addKey);

    $("#tagbuttons input").click(function() {
    if (confirm("Remove tag '" + this.name + "' from database?")) {
        $.post('/deletetagfromdb',
        { 
            "removekey" : this.name
        },
        function(data) {
            if(data["msg"]) alert(data["msg"]);
            else window.location.reload();
        },
        'json'
        );
    }
    });
});
