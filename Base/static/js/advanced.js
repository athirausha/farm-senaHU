$(document).ready(function(){

    var countries =   []
    /* FECHING EMAIL IDS OF USERS */
    $.ajax({
        type:"POST",
        url: "/email_autoconplite",
        data:{csrfmiddlewaretoken: window.CSRF_TOKEN},
        success: function( data )
        {
            console.log("AUTO COMPLETE EMAILS")
            for(i=0; i<data.email.length; i++)
            {
                countries.push(data.email[i])
            }
            console.log(countries)
        }
    });
    /* FECHING EMAIL IDS OF USERS END */

    autocomplete(document.getElementById("useremail"), countries);



    function autocomplete(inp, arr) {
        /*the autocomplete function takes two arguments, the text field element and an array of possible autocompleted values:*/
        var currentFocus;
        /*execute a function when someone writes in the text field:*/
        inp.addEventListener("input", function(e) {
            var a, b, i, val = this.value;
            /*close any already open lists of autocompleted values*/
            closeAllLists();
            if (!val) { return false;}
            currentFocus = -1;
            /*create a DIV element that will contain the items (values):*/
            a = document.createElement("DIV");
            a.setAttribute("id", this.id + "autocomplete-list");
            a.setAttribute("class", "autocomplete-items");

            /*append the DIV element as a child of the autocomplete container:*/
            this.parentNode.appendChild(a);
            /*for each item in the array...*/
            for (i = 0; i < arr.length; i++) {
                /*check if the item starts with the same letters as the text field value:*/
                if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
                    /*create a DIV element for each matching element:*/
                    b = document.createElement("DIV");
                    /*make the matching letters bold:*/
                    b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
                    b.innerHTML += arr[i].substr(val.length);
                    /*insert a input field that will hold the current array item's value:*/
                    b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
                    /*execute a function when someone clicks on the item value (DIV element):*/
                    b.addEventListener("click", function(e) {

                        /*insert the value for the autocomplete text field:*/
                        inp.value = this.getElementsByTagName("input")[0].value;

                        /*close the list of autocompleted values,(or any other open lists of autocompleted values:*/
                        closeAllLists();
                    });
                    a.appendChild(b);
                }
            }
        });

        /*execute a function presses a key on the keyboard:*/
        inp.addEventListener("keydown", function(e) {
            var x = document.getElementById(this.id + "autocomplete-list");
            if (x) x = x.getElementsByTagName("div");
            if (e.keyCode == 40) {
                /*If the arrow DOWN key is pressed,
                increase the currentFocus variable:*/
                currentFocus++;
                /*and and make the current item more visible:*/
                addActive(x);
            }
            else if (e.keyCode == 38) { //up
                /*If the arrow UP key is pressed,
                decrease the currentFocus variable:*/
                currentFocus--;
                /*and and make the current item more visible:*/
                addActive(x);
            }
            else if (e.keyCode == 13) {
                /*If the ENTER key is pressed, prevent the form from being submitted,*/
                e.preventDefault();
                if (currentFocus > -1) {
                    /*and simulate a click on the "active" item:*/
                    if (x) x[currentFocus].click();
                }
            }
        });

        function addActive(x) {
            /*a function to classify an item as "active":*/
            if (!x) return false;
            /*start by removing the "active" class on all items:*/
            removeActive(x);
            if (currentFocus >= x.length) currentFocus = 0;
            if (currentFocus < 0) currentFocus = (x.length - 1);
            /*add class "autocomplete-active":*/
            x[currentFocus].classList.add("autocomplete-active");
        }

        function removeActive(x) {
            /*a function to remove the "active" class from all autocomplete items:*/
            for (var i = 0; i < x.length; i++) {
                x[i].classList.remove("autocomplete-active");
            }
        }

        function closeAllLists(elmnt) {
            /*close all autocomplete lists in the document,
            except the one passed as an argument:*/
            var x = document.getElementsByClassName("autocomplete-items");
            for (var i = 0; i < x.length; i++) {
                if (elmnt != x[i] && elmnt != inp) {
                    x[i].parentNode.removeChild(x[i]);
                }
            }
        }

        /*execute a function when someone clicks in the document:*/
        document.addEventListener("click", function (e) {
            closeAllLists(e.target);
        });
    }

    $("#Add_user_list").click(function(){
        var email = $('#useremail').val();
        var role = $("#role").val();
        var profile = $("#profile").val();
        var table_id = $("#table_id").val();
        var report_id = $("#report_id").val();
        console.log(email);
        console.log(role);
        console.log(profile);
        $.ajax({
            type:"POST",
            url: "/user_list_update",
            data:{csrfmiddlewaretoken: window.CSRF_TOKEN, email:email, role:role, profile:profile, table_id:table_id,reports_id:report_id},
            async: false,
            success: function( data )
            {
                console.log(data);
                messages(data.Message, data.Type)
            }
         });
           setTimeout(function()
      {
        location.reload();
      }, 2000);
    });

    /* Saving NEW ROLE / Goup */
    $("#btn_creating_role").click(function(){

        var role_name = $("#role_name").val();
        var about =  $("#role_about").val();
        var add_user = 'false';
        var create_table = 'false';
        var add_data = 'false';
        var delete_data = 'false';
        var update_data = 'false';
        var add_fields = 'false';
        var delete_fields = 'false';
        var update_fields = 'false';
        var create_report = 'false';
        var view_report = 'false';
        var delete_report = 'false';

        if($("#add_user").prop('checked') == true) add_user = 'true';
        if($("#create_table").prop('checked') == true) create_table = 'true';
        if($("#add_data").prop('checked') == true) add_data = 'true';
        if($("#delete_data").prop('checked') == true) delete_data = 'true';
        if($("#update_data").prop('checked') == true) update_data = 'true';
        if($("#add_fields").prop('checked') == true) add_fields = 'true';
        if($("#delete_fields").prop('checked') == true) delete_fields = 'true';
        if($("#update_fields").prop('checked') == true) update_fields = 'true';
        if($("#create_report").prop('checked') == true) create_report = 'true';
        if($("#view_report").prop('checked') == true) view_report = 'true';
        if($("#delete_report").prop('checked') == true) delete_report = 'true';
        console.log(add_fields)
        console.log(delete_fields)
        console.log(update_fields)

        $.ajax({
            type:"POST",
            url: "/role_add",
            data:{csrfmiddlewaretoken: window.CSRF_TOKEN, role_name:role_name, about:about, add_user:add_user,
             create_table:create_table, add_data:add_data, delete_data:delete_data, update_data:update_data,
              add_fields:add_fields, delete_fields:delete_fields, update_fields:update_fields,
                delete_report:delete_report,create_report:create_report,view_report:view_report},

            success: function( data )
            {
                console.log(data);
                //messages(data.Message, data.Type)
            },
            error:function(er){
            console.log(er)
            }
        });
        setTimeout(function()
      {
        location.reload();
      }, 2000);
    });
    /* Saving NEW ROLE / Group End */


    $(document).on('change','#role_update',function(){
         var role_id = $("#role_update").val();
         $.ajax({
            type:"POST",
            url: "/role_update_fetch",
            data:{csrfmiddlewaretoken: window.CSRF_TOKEN, role_id:role_id},
            async: false,
            success: function( data )
            {
                console.log(data.Result[0]['about']);
                //messages(data.Message, data.Type)
                $("#up_role_name").val(data.Result[0]['role']);
                $("#up_role_about").val(data.Result[0]['about']);
                if (data.Result[0]['add_user'] == 'true') $('#up_add_user').prop('checked', true);
                if (data.Result[0]['create_tables'] == 'true') $('#up_create_table').prop('checked', true);
                if (data.Result[0]['add_data'] == 'true') $('#up_add_data').prop('checked', true);
                if (data.Result[0]['delete_data'] == 'true') $('#up_delete_data').prop('checked', true);
                if (data.Result[0]['update_data'] == 'true') $('#up_update_data').prop('checked', true);
                if (data.Result[0]['add_col'] == 'true') $('#up_add_fields').prop('checked', true);
                if (data.Result[0]['delete_col'] == 'true') $('#up_delete_fields').prop('checked', true);
                if (data.Result[0]['update_col'] == 'true') $('#up_update_fields').prop('checked', true);
                if (data.Result[0]['create_report'] == 'true') $('#up_create_report').prop('checked', true);
                if (data.Result[0]['view_report'] == 'true') $('#up_view_report').prop('checked', true);
                if (data.Result[0]['delete_report'] == 'true') $('#up_delete_report').prop('checked', true);

            }
         });

        $(".div_vs").removeClass("role_updateion_div");
        $(".div_vs").addClass("role_updateion_div_visible");
    });

    $("#btn_update_role").click(function(){
        var role_id = $("#role_update").val();
        var role_name = $("#up_role_name").val();
        var about =  $("#up_role_about").val();
        var add_user = 'false';
        var create_table = 'false';
        var add_data = 'false';
        var delete_data = 'false';
        var update_data = 'false';
        var add_fields = 'false';
        var delete_fields = 'false';
        var update_fields = 'false';
        var create_report = 'false';
        var view_report = 'false';
        var delete_report = 'false';

        if($("#up_add_user").prop('checked') == true) add_user = 'true';
        if($("#up_create_table").prop('checked') == true) create_table = 'true';
        if($("#up_add_data").prop('checked') == true) add_data = 'true';
        if($("#up_delete_data").prop('checked') == true) delete_data = 'true';
        if($("#up_update_data").prop('checked') == true) update_data = 'true';
        if($("#up_add_fields").prop('checked') == true) add_fields = 'true';
        if($("#up_delete_fields").prop('checked') == true) delete_fields = 'true';
        if($("#up_update_fields").prop('checked') == true) update_fields = 'true';
        if($("#up_create_report").prop('checked') == true) create_report = 'true';
        if($("#up_view_report").prop('checked') == true) view_report = 'true';
        if($("#up_delete_report").prop('checked') == true) delete_report = 'true';

        $.ajax({
            type:"POST",
            url: "/role_update",
            data:{csrfmiddlewaretoken: window.CSRF_TOKEN, role_name:role_name, about:about, add_user:add_user,
             create_table:create_table, add_data:add_data, delete_data:delete_data, update_data:update_data,
              add_fields:add_fields, delete_fields:delete_fields, update_fields:update_fields, role_id:role_id,
              delete_report:delete_report,create_report:create_report,view_report:view_report},

            success: function( data )
            {
                console.log(data);
                //messages(data.Message, data.Type)
            },
            error:function(er){
            console.log(er)
            }
        });
        setTimeout(function()
      {
        location.reload();
      }, 2000);
    });

});


function messages(messages, clr)
{
    $.notify({
        message: "<strong>"+messages+"</strong>"
    },
    {
        type: clr
    });
}

    $(function() {
    var nContainer = $(".notification-popup-container");

    //notification popup
    $("#notification-link").click(function() {
        nContainer.toggle();
        return false;
    });

    //page click to hide the popup
    $(document).click(function() {
        nContainer.hide();
    });

    //popup notification bubble on click
    nContainer.click(function() {
        return false;
    });
});
// /* UPDATE USER*/
var adminid;

$(document).on('change','#pro_update',function(){
    var sel_value=[];
    var sel_report_value=[];
    var pro_id = $("#pro_update option:selected").html();
    console.log(pro_id)
    var created_user = $("#pro_update option:selected").val();
    console.log('user'+created_user)
    $.ajax({
       type:"POST",
       url: "/pro_update_fetch",
       data:{csrfmiddlewaretoken: window.CSRF_TOKEN, pro_id:pro_id,admin_id:created_user},
       async: false,
       success: function( data )
       {
           console.log(data)
           console.log(data.Result.length)
           console.log(data.Result[0]['role']);
           console.log('adminid'+data.Result[0]['admin_id']);

          adminid=data.Result[0]['admin_id']

           $("#up_role").val(data.Result[0]['role']).prop('selected',true);
           $("#up_profile").val(data.Result[0]['profile']).prop('selected',true);

           for(i=0;i<data.Result.length;i++)

            {
            //  console.log(data.Result[i]['table_id'])

              sel_value.push(data.Result[i]['table_id'])
              sel_report_value.push(data.Result[i]['report_id'])
              $("#up_table_id").val(sel_value).prop('selected',true);
              $("#up_report_id").val(sel_report_value).prop('selected',true);

            }
            console.log('sel_value'+sel_value)
            $("#up_table_id").selectpicker("refresh");
            $("#up_report_id").selectpicker("refresh");


       }
    });

//   $(".div_pro").removeClass("pro_updateion_div");
//   $(".div_pro").addClass("pro_updateion_div_visible");
});

$("#btn_update_pro").click(function(){
    var table_name=[];
    var report_name=[];
    var pro_id = $("#pro_update option:selected").html();
    var role_name = $("#up_role option:selected").val();
    var profile =  $("#up_profile option:selected").val();

    tbl_name=$("#up_table_id option:selected ").map(function(){return $(this).val();}).get();
    console.log('table_name'+tbl_name)
    report_name=$("#up_report_id option:selected ").map(function(){return $(this).val();}).get();
    console.log('table_name'+report_name)


    // console.log('select_option_length'+select_option_length)
     console.log('admin_id'+ adminid)


    $.ajax({
        type:"POST",
        url: "/pro_update",
        data:{csrfmiddlewaretoken: window.CSRF_TOKEN, role_name:role_name, pro_id:pro_id,profile:profile,
                                                tbl_name:tbl_name,adminid:adminid,report_id:report_name},
        success: function(data)
        {
            console.log(data);

        },
        error:function(er){
        console.log(er)
        }
    });
     setTimeout(function()
  {
    location.reload();
  }, 2000);


});

$('.delete_userss').click(function(){
console.log($(this).attr('id'))
console.log(adminid)
$.ajax({
    url:'/delete_userfrom_userlist',
    type:'POST',
    data:{csrfmiddlewaretoken: window.CSRF_TOKEN,userid:$(this).attr('id')},
    success:function(data){
        window.location.href = "/load_reportpage";
    },
}); setTimeout(function(){location.reload();}, 2000);
});

/* CreateProfile*/
$('#profile_create').click(function(){
profile=$('#userprofile').val()
console.log(profile)
$.ajax({
    url:'/create_users_profle',
    type:'POST',
    data:{csrfmiddlewaretoken: window.CSRF_TOKEN,profile:profile},
    success:function(data){

    },
}); setTimeout(function(){location.reload();}, 2000);
});
/* CreateProfile end */

