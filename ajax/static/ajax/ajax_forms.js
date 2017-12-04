function updateSections(django_url, machine, section){
    $.ajax({
        method: "POST",
        url: django_url,
        section: section, //custom variable
        data: {
            "machine": machine,
        },
        success: function(result){
            var sections =  "<option value=''>-Select Section-</option> ";

    for(i in result.sections){
        sections += "<option value='*'>".replace('*', result.sections[i][0]) + result.sections[i][1] + "</option>";
        
    }

    this.section.html(sections); // custom variable 
        }
    });

}


function updateSubUnits(django_url, section, subunit){
        $.ajax({
            method: "POST",
            url: django_url,
            subunit:subunit, //custom variable
            data: {
                "section": section,
            },
            success: function(result){
                var units =  "<option value=''>-Select SubUnit-</option> ";

        for(i in result.units){
            units += "<option value='*'>".replace('*', result.units[i][0]) + result.units[i][1] + "</option>";
            
        }

        this.subunit.html(units); // custom variable 
            }
        });
    
    }


function updateSubAssemblies(django_url, unit, subassembly){
    $.ajax({
            method: "POST",
            url: django_url,
            subassembly: subassembly,
            data: {
                "unit": unit,
            },
            success: function(result){
                var units =  "<option value=''>-Select SubAssembly-</option> ";

        for(i in result.subassemblies){
            units += "<option value='*'>".replace('*', result.subassemblies[i][0]) + result.subassemblies[i][1] + "</option>";
            
        }
        this.subassembly.html(units); // that is its children
            }
        });

    }

function updateComponents(django_url, subassembly, component){
    $.ajax({
            method: "POST",
            url: django_url,
            component: component,
            data: {
                "subassy": subassembly,
            },
            success: function(result){
                var units =  "<option value=''>-Select Component-</option> ";

        for(i in result.components){
            units += "<option value='*'>".replace('*', result.components[i][0]) + result.components[i][1] + "</option>";
            
        }
        this.component.html(units); // that is its children
            }
        });

    }
// reuse if necessary
function ajaxAuthenticate(django_url, user, pwd){
    $.ajax({
            method: "POST",
            url: django_url, 
            data: {
                    "username": $("#user").val(),
                    "password":$("#password").val(),
                },
                success: function(result){
                    return result["authenticated"]
                }
            }); 
    }