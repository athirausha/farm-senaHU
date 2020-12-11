$(document).ready(function () {



    // Sidemenubar Script
    $("#toggle-btn").click(function () {
        $(".side-menu").toggleClass("side-menu-xm");
        $(".wrapper").toggleClass("wrapper-xm");
        $(".header").toggleClass("header-xm");

    });

    // Data Table Script
    $('#myTable').DataTable({
        "order": [[3, "desc"]]
    });


    //Tooltip Script

    tooltip();
    openSidebar();
    closeSidebar();
    function openSidebar(){
    $("#more-subs").on('click', function(){
        $(".sidebar-right").addClass("active");
    })
    }
    function closeSidebar(){
    $(".sidebar-close").on('click', function(){
        $(".sidebar-right").removeClass("active");
    })
}


    var hash = document.location.hash;
    if (hash) {
        console.log(hash);
        $(".nav-tabs a[href=\\" + hash + "]").tab('show');
    }

    // Change hash for page-reload
    $('.nav-tabs a').on('shown.bs.tab', function (e) {
        window.location.hash = e.target.hash;
    });






    // Delete table row

    $('.column_table').on('click', '.delete-col-table', function (e) {
        $(this).closest('tr').remove();
    })


    $('.reference_table').on('click', '.delete-ref-table', function (e) {
        $(this).closest('tr').remove();
    })


    //select option function call appened row
    $(document).on('click', '#add-row', function () {
        tooltip()
    })

    $(document).on('click', '#add-row-ref', function () {
        tooltip()
    })



     //clone new table row
    let lineNo = 2;
    $("#add-row").click(function () {

         markup = "<tr><td>" + lineNo + "</td><td><div class='form-group m-0'><input type='text' class='form-control' placeholder='Business Name' name='baycol_add'></div></td><td><div class='form-group m-0'><input type='text' class='form-control' placeholder='Techinical Name' name='tech_name'></div></td><td><div class='form-group'><select class='form-control' name='coldatatype'> <option value='String'>String</option><option value='Date'>Date</option><option value='Time'>Time</option><option value='Number'>Number</option><option value='Image'>Image</option></select></div></td><td><div class='form-group m-0'><input type='text' class='form-control' placeholder='Size' name='sizee'></div></td><td><div class='form-group'><select class='form-control' name='noyes'><option value='NOTNULL'>Not-Null</option> <option value='NULL'>Null</option></select></div></td><td><div class='actions'> <a class='delete delete-col-table' data-toggle='tooltip' data-placement='top' title='Delete'><i class='fa fa-trash-o' aria-hidden='true'></i></a></div></td></tr>";
       tableBody = $(".column_table tbody");
        tableBody.append(markup);
        lineNo++;
    });




    let lineNoref = 2;
    let tmp_main = "<option value='0'>Select...</option>"
    $("#add-row-ref").click(function () {
        $.ajax({
            url: '/relation_maters',
            type: 'POST',
            data: {csrfmiddlewaretoken: window.CSRF_TOKEN},
            async: false,
            success: function (data)
            {
                console.log(data);
                for(i=0; i<data.Result.length; i++)
                {
                  console.log(data.Result[i]);

                    var tmp = "<option value='"+data.Result[i].pk+"'>"+data.Result[i].base_name+"</option>";
                    tmp_main = tmp_main+tmp;
                    alert(tmp);

                }
            },
            error:function(e)
            {
                console.log(e)
            }
          });
        alert(tmp_main);
        markup = "<tr><td>" + lineNoref + "</td><td><div class='form-group m-0'><select class='form-control' id='master_table_relation_select'>"+tmp_main+"</select></div></td><td>  <div class='form-group m-0'><select  class='form-control' id='master_table_relation_column_select'></select></div></td><td><div class='actions'> <a class='delete delete-ref-table' data-toggle='tooltip' data-placement='top' title='Delete'><i class='fa fa-trash-o' aria-hidden='true'></i></a></div></td></tr>";
        tableBody = $(".reference_table tbody");
        tableBody.append(markup);
        lineNoref++;

    });


});





    function tooltip() {
        $(function () {
            $('[data-toggle="tooltip"]').tooltip({
                trigger: 'hover'
            })
        })
        $('[data-toggle="tooltip"]').click(function () {
            $('[data-toggle="tooltip"]').tooltip("hide");
        });
    }
// Date script
document.getElementById("date").innerHTML = formatAMPM();
function formatAMPM() {
    var d = new Date(),
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    return days[d.getDay()] + ' ' + d.getDate() + '  ' + months[d.getMonth()] + ' ' + d.getFullYear();
}

var $dOut = $('#date'),
    $hOut = $('#hours'),
    $mOut = $('#minutes'),
    $sOut = $('#seconds'),
    $ampmOut = $('#ampm');

function update() {
    var date = new Date();

    var ampm = date.getHours() < 12
        ? 'AM'
        : 'PM';

    var hours = date.getHours() == 0
        ? 12
        : date.getHours() > 12
            ? date.getHours() - 12
            : date.getHours();

    var minutes = date.getMinutes() < 10
        ? '0' + date.getMinutes()
        : date.getMinutes();

    var seconds = date.getSeconds() < 10
        ? '0' + date.getSeconds()
        : date.getSeconds();



    $hOut.text(hours);
    $mOut.text(minutes);
    $sOut.text(seconds);
    $ampmOut.text(ampm);
}

update();
window.setInterval(update, 1000);

//clone new table row in ref
 let lineNo = 2;
 $("#refrance_model_save").click(function () {
     ref_table=$('.tblref option:selected').html()
     ref_val=$('.tblref option:selected').val()
     console.log(ref_val)
     console.log('ref_val')
     column_ref=$('.colref option:selected').html()
     console.log(column_ref)
     col_val=$('.colref option:selected').val()
     if(ref_val != 0 && col_val != 0 )
     {
    markup = "<tr><td>" + lineNo + "<td><div class='form-group m-0'><select  class='form-control' id='master_table_relation_select'><option value='selected'>"+ref_table+"</option></select></div></td><td><div class='form-group m-0'><select  class='form-control' id='master_table_relation_column_select'><option value='0'>"+column_ref+"</option></select></div></td><td><div class='actions'><a class='delete delete-ref-table' data-toggle='tooltip' data-placement='top' title='Delete'><i class='fa fa-trash-o' aria-hidden='true'></i></a></div></td>";
     tableBody = $(".reference_table tbody");
     tableBody.append(markup);
     lineNo++;
    }
    else{
        new Noty({
            type: 'error',
            layout: 'topRight',
            theme: 'metroui',
            text: 'Required fields cannot be empty. ! 🤖',
            timeout: '2000',
            progressBar: true,
            closeWith: ['click'],
            killer: true,

         }).show();
    }
 });

