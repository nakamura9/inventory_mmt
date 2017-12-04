/*My js refactor
functions

1. saferId(str) makes sure the id's are valid.
2. addHiddenInput(id, name, v) simplifies the process of supplying aux data to a form
3. addItemToList(list, value, id, callback) creates a consistent div with a delete button
4. updateDatalist(source, model, datalist) performs ajax request to update a datalist
5. checkInput(list_id) validates the value submitted in a for returns bool*/



function saferId(str, partial){
    //check if id exists
    var str = str.toString();
    if(str == ""){
        alert("The input is invalid");
        return null;
    }
    var val = str.split(" ").join("-");
    _check = $("#" + val);
    if(_check.length && !(partial)){
        //find a way to reject some duplicates
        console.log("There is an element that already has this id");
        return null;
    }
    return val;
}


function addHiddenInput(id, name, v){
    if(saferId(id)){
        $("<input>").attr({
            type: "hidden",
            id: saferId(id, false),
            name: name,
            value: v
        }).appendTo("form");
    }
}


function addItemToList(list, value, id, callback){
   /* This function generalizes the common task of creating a
    div element used to list data for a certain operation e.g. 
    a list of tasks or a list of spares etc
    
    Parameters
    -----------
    
    Input:
        list -> id of a div the element will be appended to
        value -> the content of the element
        attrs -> the attributes of the new element
    */
    var block;
    var block_content;
    var dismiss_button;
    var id_tail= saferId(id, true);
    if(!id_tail){
        alert("Invalid value");
        return null;
    }
    var block_id = saferId(list + "_item_" + id_tail, false);
    if(!block_id){
        return null;
    }
    block = $("<div>").attr({
        "id": block_id
    });
    
    block.css({
        "min-height": "40px",
        "background-color": "#ccc",
        "min-width": "200px",
        "margin": "2px",
        "padding": "3px",
    });

    dismiss_button = $("<button>").attr({
        "class": "btn btn-default",
        "type": "button"
    });
    dismiss_button.html(
        $("<span>").attr({
            "class": "glyphicon glyphicon-remove",
            "aria-hidden": "true"
        }));
    dismiss_button.attr({"onclick": callback});
    
    block_content =$("<span>").attr({
        "style": "float:right;"
    }).html(dismiss_button);

    
    block.append(value);
    block.append(block_content);
    console.log(block);
    $("#"+ list).append(block);

}

function updateDatalist(source, model, datalist){
    $("#" + datalist).html("");
    $.ajax({
        url: "/ajax/get-combos/",
        data: {"str": $("#"+ source).val(),
                "model": model},
        method:"POST",
        success: function(result){
        
            for(i in result.matches){
                var opt =$("<option>").attr({
                    "value": result.matches[i]
                }).text(result.matches[i]); 
                
                $("#" + datalist).append(opt);
            } 
            
        }

    })
}

function checkInput(list_id){
    //function to validate datalist entry

    var input = $("#" + list_id);
    var val = $("#" + list_id).val();
    var list = input.attr("list");

    match = $("#"+list+ " option").filter(function(){
        return ($(this).val() == val);
    });
    if(match.length > 0){
        return true;
    }else{
        alert("Please select a value from the list");
        return false;
    }
}