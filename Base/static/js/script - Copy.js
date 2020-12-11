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
    $(function () {
        $('[data-toggle="tooltip"]').tooltip({
              trigger : 'hover'
        })
    })
    
    $('[data-toggle="tooltip"]').click(function () {
         $('[data-toggle="tooltip"]').tooltip("hide");
     });
    

    var hash = document.location.hash;
    if (hash) {
        console.log(hash);
        $(".nav-tabs a[href=\\" + hash + "]").tab('show');
    }

    // Change hash for page-reload
    $('.nav-tabs a').on('shown.bs.tab', function (e) {
        window.location.hash = e.target.hash;
    });


    // Custom select option
    $('select.custom-select-ref').each(function () {
       var $this = $(this),
        numberOfOptions = $(this).children('option').length;

        $this.addClass('select-hidden');
        $this.wrap('<div class="select"></div>');
        $this.after('<div class="select-styled"></div>');

        var $styledSelect = $this.next('div.select-styled');
        $styledSelect.text($this.children('option').eq(0).text());

        var $list = $('<ul />', {
            'class': 'select-options'
        }).insertAfter($styledSelect);

        for (var i = 0; i < numberOfOptions; i++) {
            $('<li />', {
                text: $this.children('option').eq(i).text(),
                rel: $this.children('option').eq(i).val()
            }).appendTo($list);
        }

        var $listItems = $list.children('li');

        $styledSelect.click(function (e) {
            e.stopPropagation();
            $('div.select-styled.active').not(this).each(function () {
                $(this).removeClass('active').next('ul.select-options').hide();
            });
            $(this).toggleClass('active').next('ul.select-options').toggle();
        });

        $listItems.click(function (e) {
            e.stopPropagation();
            $styledSelect.text($(this).text()).removeClass('active');
            $this.val($(this).attr('rel'));
            $list.hide();
            console.log($this.val());
        });

        $(document).click(function () {
            $styledSelect.removeClass('active');
            $list.hide();

        });
    });
    



    // Delete table row
    
        $('.column_table').on('click', '.delete-col-table', function (e) {
        $(this).closest('tr').remove();
        })
    
    
        $('.reference_table').on('click', '.delete-ref-table', function (e) {
        $(this).closest('tr').remove();
        })
    
    
     $(".select-styled").click(function(){
        $(".select-options").toggleClass("main");
      });



    // clone new table row
    let lineNo = 2;
    $("#add-row").click(function () {
        
        markup = "<tr><td>" + lineNo + "</td><td><div class='actions'>  <a class='edit edit-col-table' data-toggle='tooltip' data-placement='top' title='Edit' ><img src='img/edit.svg'></a><a class='delete delete-col-table' data-toggle='tooltip' data-placement='top' title='Delete'><img src='img/delete.svg'></a></div></td><td><div class='form-group m-0'><input type='text' class='form-control' placeholder='Business Name'></div></td><td><div class='form-group m-0'><input type='text' class='form-control' placeholder='Techinical Name'></div></td><td><div class='form-group'><select class='form-control custom-select-ref'><option value='string'>String</option><option value='number'>Number</option><option value='decimal'>Decimal</option></select></div></td></tr>"; 
        tableBody = $(".column_table tbody");
        tableBody.append(markup);
        lineNo++;
    });
    
    
    let lineNoref = 2;
     $("#add-row-ref").click(function () {
        markup = "<tr><td>" + lineNoref + "</td><td><div class='actions'>  <a class='edit edit-col-table' data-toggle='tooltip' data-placement='top' title='Edit'><img src='img/edit.svg'></a><a class='delete delete-ref-table' data-toggle='tooltip' data-placement='top' title='Delete'><img src='img/delete.svg'></a></div></td><td><div class='form-group m-0'><select  class='form-control custom-select-ref' ><option>Select1</option><option>Select2</option><option>Select3</option></select></div></td><td><div class='form-group m-0'><select  class='form-control custom-select-ref'><option>Select1</option><option>Select2</option><option>Select3</option></select></div></td></tr>"; 
        tableBody = $(".reference_table tbody");
        tableBody.append(markup);
        lineNoref++;
    });


});




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
