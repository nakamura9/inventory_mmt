function updateSubUnits(django_url, machine, subunit){
        $.ajax({
            method: "POST",
            url: django_url,
            subunit: subunit, //custom variable
            data: {
                "machine": machine,
            },
            success: function(result){
                var units =  "<option value='None'>-Select SubUnit-</option> ";

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
                var units =  "<option value='None'>-Select SubAssembly-</option> ";

        for(i in result.subassemblies){
            units += "<option value='*'>".replace('*', result.subassemblies[i][0]) + result.subassemblies[i][1] + "</option>";
            
        }
        this.subassembly.html(units); // that is its children
            }
        });

    }