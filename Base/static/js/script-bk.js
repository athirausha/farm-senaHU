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
    function tooltip(){
         $(function () {
        $('[data-toggle="tooltip"]').tooltip({
              trigger : 'hover'
        })
    })
    $('[data-toggle="tooltip"]').click(function () {
         $('[data-toggle="tooltip"]').tooltip("hide");
     });
    }
   tooltip()
    

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
    
    
//     $(".select-styled").click(function(){
//        $(".select-options").toggleClass("main");
//      });

    
    //Custom Select option
    $('select.form-control').selectpicker('refresh');
    
    
   
 

    //select option function call appened row
   $(document).on('click','#add-row',function(){
       $('select.form-control').selectpicker('render');
       tooltip()
   })
    
    $(document).on('click','#add-row-ref',function(){
       $('select.form-control').selectpicker('render');
        tooltip()
   })
    
     $(document).on('click','#add-row-ref',function(){
        //multi();
         multi1(lineNoref)
    })
    
    // clone new table row
    let lineNo = 2;
    $("#add-row").click(function () {
        
        markup = "<tr><td>" + lineNo + "</td><td><div class='actions'>  <a class='edit edit-col-table' data-toggle='tooltip' data-placement='top' title='Edit' ><img src='img/edit.svg'></a><a class='delete delete-col-table' data-toggle='tooltip' data-placement='top' title='Delete'><img src='img/delete.svg'></a></div></td><td><div class='form-group m-0'><input type='text' class='form-control' placeholder='Business Name'></div></td><td><div class='form-group m-0'><input type='text' class='form-control' placeholder='Techinical Name'></div></td><td><div class='form-group'><select class='form-control selectpicker'><option value='string'>String</option><option value='number'>Number</option><option value=decimal>Decimal</option></select></div></td></tr>"; 
        tableBody = $(".column_table tbody");
        //$('select.form-control').selectpicker();
        tableBody.append(markup);
        lineNo++;
    });
    
   
    
    
    let lineNoref = 2;
    let selectref = 3;
    let selectrefse =4;
     $("#add-row-ref").click(function () {
        markup = "<tr><td>" + lineNoref + "</td><td><div class='actions'>  <a class='edit edit-col-table' data-toggle='tooltip' data-placement='top' title='Edit'><img src='img/edit.svg'></a><a class='delete delete-ref-table' data-toggle='tooltip' data-placement='top' title='Delete'><img src='img/delete.svg'></a></div></td><td><div class='form-group m-0'><div class='input-group'><div class='input-group-btn'><button type='button' class='btn dropdown-toggle' data-toggle='dropdown'><span class='caret'></span></button><ul id='demolist1' class='dropdown-menu'><li><a href='#'>A</a></li><li><a href='#'>B</a></li><li><a href='#'>C</a></li></ul></div></div></div></td><td>  <div class='form-group m-0'><select id='choice"+selectrefse+"' name='select2' class='form-control selectpicker'><option data-option='1' value='1'>Select1-1</option><option data-option='1' value='1'>Select2-1</option><option data-option='1' value='1'>Select3-1</option><option data-option='2' value='2'>Select1-2</option><option data-option='2' value='2'>Select2-2</option><option data-option='2' value='2'>Select3-2</option><option data-option='3' value='3'>Select1-3</option><option data-option='3' value='3'>Select2-3</option><option data-option='3' value='3'>Select3-3</option></select></div></td></tr>"; 
        tableBody = $(".reference_table tbody");
        tableBody.append(markup);
        lineNoref++;
         selectref++;
         selectrefse++;
    });

    // Function call for multiselect
    multi();
    //multi1()
  


});

function multi(){
        //   $("#choice1").change(function () {
        //     if (typeof $(this).data('options') === "undefined") {
        //         /*Taking an array of all options-2 and kind of embedding it on the select1*/
        //         $(this).data('options', $('#choice2 option').clone());
        //     }
        //     var id = $(this).val();
        //     var options = $(this).data('options').filter('[data-option=' + id + ']');
        //     $('#choice2').html(options);
        //     $('#choice2').selectpicker('refresh');
        // })
    }

    $('#demolist1 li a').on('click', function(){
        var choice1=$('#demolist1').val($(this).html()).val();
        console.log(choice1)
        var a1=['A1','A2','A3','A4'];
        var b1=['B1','B2','B3','B4'];
        var c1=['C1','C2','C3','C4'];
      populateData(choice1,a1,b1,c1)


    });

    function populateData(choice1,a1,b1,c1)
    {
        $(".delete").remove();
        //console.log("clear");
        if(choice1=='A')
        {
            var Html="";
            $.each(a1, function( index, value ) {
                console.log( index + ": " + value );
                Html+="<li class='delete' id='"+index+"'><a href='#'>"+value+"</a></li>";

              });
             
              $("#domolist2Li").after(Html)
            

        }

        if(choice1=='B')
        {
            var Html="";
            $.each(b1, function( index, value ) {
                console.log( index + ": " + value );
                Html+="<li class='delete' id='"+index+"'><a href='#'>"+value+"</a></li>";

              });
             
              $("#domolist2Li").after(Html)
            

        }

        if(choice1=='C')
        {
            var Html="";
            $.each(c1, function( index, value ) {
                console.log( index + ": " + value );
                Html+="<li class='delete' id='"+index+"'><a href='#'>"+value+"</a></li>";

              });
             
              $("#domolist2Li").after(Html)
            

        }

    }
    
 
function multi1(lineNoref){
       
        
    
          $("#choice"+selectref+"").change(function () {
            if (typeof $(this).data('options') === "undefined") {
                /*Taking an array of all options-2 and kind of embedding it on the select1*/
                $(this).data('options', $('#choice4 option').clone());
            }
            var id = $(this).val();
            var options = $(this).data('options').filter('[data-option=' + id + ']');
            $('#choice"+selectrefse+"').html(options);
            $('#choice"+selectrefse+"').selectpicker('refresh');
        })
    }


// Date script
document.getElementById("date").innerHTML = formatAMPM();
function formatAMPM() {
var d = new Date(),
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
    days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
return days[d.getDay()]+' '+d.getDate()+'  '+months[d.getMonth()]+' '+d.getFullYear();
}

var $dOut = $('#date'),
    $hOut = $('#hours'),
    $mOut = $('#minutes'),
    $sOut = $('#seconds'),
    $ampmOut = $('#ampm');

function update(){
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
