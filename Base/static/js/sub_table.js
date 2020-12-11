sub_table_genaric_id = 0;
check_sub_table_or_main  = 0;
$(document).ready(function(){
    $(document).on('click','.sub_table_row_delete',function(){
        var ids_sub_table = [];
        var children = $(this).closest('tr').children('td.sub_td');
        for (var i = 0, len = children.length ; i < len; i++) {
            ids_sub_table.push(children[i].id);
        }
        console.log(ids_sub_table);

        var base_id = sub_table_genaric_id;

        for(i =0; i<ids_sub_table.length; i++)
        {
            $.ajax({
                url: '/delete_row',
                type: 'POST',
                data: {csrfmiddlewaretoken: window.CSRF_TOKEN, id:ids_sub_table[i], base_id:base_id},
                success: function (res) {
                },
                error: function (err) {
                    console.log(err);
                }
            });
        }
        $(this).closest('tr').remove();
    });

    /* OPENING EDIT MODEL FOR SUBTABLE */
    $(document).on('click','.sub_table_row_edite',function(){
        var ids_sub_table = [];
        var children = $(this).closest('tr').children('td.sub_td');
        for (var i = 0, len = children.length ; i < len; i++) {
            ids_sub_table.push(children[i].id);
        }
        console.log(ids_sub_table);
        row_val=[];
        relation=[];
        $('#myModal123').modal('show');
        $('.copy_details_sub_table').empty();

        var mx = $(".sub_tables_main").attr('id');
        var base_id = sub_table_genaric_id;
        var relation_primary = $(".addcol_additional th").map(function(){return $(this).attr('id');}).get();
        var relation = removeDuplicate(relation_primary);
        console.log("relation : " + relation);
        console.log('ids : ' + ids_sub_table);
        console.log('row_num : ' + mx);
        console.log("relation_length : " + relation.length);
        console.log("table id : " + base_id);
        for(i=0;i<relation.length;i++)
        {
            var txt = $('#'+ids[i]).text().trim();
            console.log(txt)

            $.ajax({
            url:'/inline_type',
            type:'POST',
            async: false,
            data:{csrfmiddlewaretoken: window.CSRF_TOKEN, key:ids_sub_table[i], base_id:base_id},
            success:function(data)
                {
                    console.log("**********");
                    console.log(data.col_pk)
                    console.log('**********');
                    if (data.Result[0].d_type.trim() == 'Date')
                    {
                        inline_type = 'Date';
                    }
                    else if (data.Result[0].d_type.trim() == 'Time')
                      {
                          inline_type = 'Time';

                      }
                    else if(data.Result[0].d_type.trim() == 'Calc')
                    {
                        inline_type = 'Calc';
                    }
                    else if(data.Result[0].d_type.trim() == 'Text' || data.Result[0].d_type.trim() == 'Numeric'|| data.Result[0].d_type.trim() == 'Number'|| data.Result[0].d_type.trim() == 'String')
                    {
                      inline_type = 'text';
                    }
                    else if(data.Result[0].d_type.trim() == 'Image')
                     {
                          inline_type = 'File';
                     }
                    else
                    {
                      inline_type = "select"
                    }


                    console.log("Inline Type : " + inline_type)

                    if(inline_type == 'select')
                    {
                        st = '<div class="col-md-12"><label>'+data.Result[0].c_name+'</label> <select class="details_edit_sub_table form-control rr_edit" name="'+ data.Result[0].pk +'" id="'+ data.col_values[0].pk +'">';
                        for(j=0; j<data.Relation.length; j++)
                        {
                            console.log(data.Relation.length)
                            if(data.Relation[j] == col_val_names_sub_table.trim())
                            {
                                st = st + '<option value="'+data.Relation[j]+'">'+data.Relation[j]+'</option>';
                            }
                        }
                        st = st + '</select></div>';
                        $('.copy_details_sub_table').append(st);
                    }
                    else if(inline_type == 'Calc')
                    {
                        console.log("Inline type is Calc")
                        var div = "<div class='col-md-12'>"
                        var c_div="</div>";
                        $('.copy_details_sub_table').append(div + '<label>' + data.Result[0].c_name + '</label> <input type="'+inline_type+'" value="'+ data.col_values[0].c_v +'" class="inlinetxt  detailid_clc_edit form-control max" name="'+ data.Result[0].pk +'" id="'+ data.col_values[0].pk +'" disabled maxlength="'+data.Result[0].d_size+'">' + c_div);
                    }
                    else if(inline_type == 'File')
                    {
                        var div="<div class='col-md-12'>"
                        var c_div="</div>"
                        $('.copy_details_sub_table').append(''+div+'<div class="row"><div class="col-md-3"><label>'+data.Result[0].c_name+'</label></div><div class="col-md-6" ><form method="POST" enctype="multipart/form-data" class="model_edit_fileUploadForm_images_data_sub_table"><input type="file" class="inlinetxt  form-control model_edit_detailid_add_new_image_sub_table max" name="files" id="'+ data.col_values[0].pk +'"></form></div><div class="col-md-3"><img class="td_image" src="'+ data.col_values[0].c_v +'" alt="Image"></div></div>'+c_div+'');


                    }
                    else
                    {
                        var div="<div class='col-md-12'>"
                        var c_div="</div>"
                        $('.copy_details_sub_table').append(''+div+'<label>'+data.Result[0].c_name+'</label> <input name="'+ data.Result[0].pk +'" type="'+inline_type+'" value="'+data.col_values[0].c_v+'" class="inlinetxt details_edit_sub_table form-control max" id="'+ data.col_values[0].pk +'" maxlength="'+data.Result[0].d_size+'">'+c_div+'');

                    }
                }
            });
        }
        /* OPENING EDIT MODEL FOR SUB TABLE END */


        $('.edit_modal_sub_table').click((e)=>{
            var relation_primary = $(".details_edit_sub_table").map(function(){return $(this).attr('name');}).get();
            var relation = removeDuplicate(relation_primary);
            var values= $(".details_edit_sub_table").map(function(){return $(this).val();}).get();
            var data_pk = $(".details_edit_sub_table").map(function(){return $(this).attr('id');}).get();
            var table_id = sub_table_genaric_id;
            var mx = $(".sub_tables_main").attr('id');

            console.log("relation : " + relation);
            console.log("values : " + values);
            console.log("data_pk : " + data_pk);
            console.log("table_id : " + table_id);
            console.log("mx : " + mx);

            for(i=0;i<relation.length;i++)
            {
                console.log(values[i]);
                console.log(data_pk[i])
                $.ajax({
                    url:'/edit_modal',
                    type:'POST',
                    async: false,
                    data:{csrfmiddlewaretoken: window.CSRF_TOKEN, key:data_pk[i], value:values[i], table_id:table_id}
                });
            }

            /** Image data upload **/
            console.log("--- Uploading Images ---")
            var image_columns_id = $(".model_edit_detailid_add_new_image_sub_table").map(function(){return $(this).attr('id');}).get();
            var form_data_image = $(".model_edit_fileUploadForm_images_data_sub_table").map(function(){return $(this)[0];}).get();
            console.log("image_columns_id : - ");
            console.log(image_columns_id);
            console.log("form_data_image : -");
            console.log(form_data_image);
            for(i=0; i<image_columns_id.length; i++)
            {
                var form = form_data_image[i];
                var data = new FormData(form);
                data.append("id", image_columns_id[i]);
                data.append('base_id', sub_table_genaric_id);
                data.append("csrfmiddlewaretoken", window.CSRF_TOKEN);
                $.ajax({
                    type:'POST',
                    enctype: 'multipart/form-data',
                    url:'/inline_update_image',
                    async:false,
                    data:data,
                    processData: false,
                    contentType: false,
                    cache: false,
                    timeout: 600000,
                    success: function( data ){
                        console.log(data);
                    }
                });
            }
            /** Image data upload end **/
            loading_tables();
            $("#myModal123").modal('hide');

        });

    });



    $(document).on('click','.new_row_add_sub_table',function(){
        relation = [];
        row_val= [];

        var relation = $(".addcol_additional tr:first th").map(function(){return $(this).attr('id');}).get();
        var row_val =$(".addcol_additional tr:first th").map(function(){return $(this).text().trim();}).get();
        var base_id = sub_table_genaric_id;
        console.log("relation : " + relation);
        console.log("row_val : " + row_val);
        console.log(relation.length);


        var st ='<tr>';

        for(i=0;i<relation.length;i++)
        {
            $.ajax({
              url:'/inline_type_sub_table',
              type:'POST',
              async: false,
              data:{csrfmiddlewaretoken: window.CSRF_TOKEN, key:relation[i], base_id:base_id},
              success:function(data)
                  {
                      console.log('-------------------------------------------');
                      console.log(data)

                      if (data.Result[0].d_type.trim() == 'Date')
                      {
                          inline_type = 'Date';

                      }
                      else if (data.Result[0].d_type.trim() == 'Time')
                      {
                            inline_type = 'Time';
                      }
                      else if(data.Result[0].d_type.trim() == 'Calc')
                      {
                          inline_type = 'Calc';
                      }
                      else if(data.Result[0].d_type.trim() == 'Text' || data.Result[0].d_type.trim() == 'Numeric'|| data.Result[0].d_type.trim() == 'Number'|| data.Result[0].d_type.trim() == 'String')
                      {
                          inline_type = 'text';
                      }
                      else if(data.Result[0].d_type.trim() == 'Image')
                      {
                          inline_type = 'File';
                      }
                      else
                      {
                          inline_type ="select"
                      }
                       console.log("Inline Type : "+ inline_type);


                      if(inline_type == 'select')
                      {
                          st = st + '<td><select class="inlinetxt form-control rr detailid_clone" id="'+data.Result[0].pk+'" name="'+ data.Result[0].nul_type +'">';
                          console.log("*******************");
                          console.log(data.Relation)
                          console.log(data.Relation.length);

                          for(j=0; j<data.Relation.length; j++)
                          {
                              console.log(data.Relation[i]);
                              if(data.Result[0].pk == col_val_id_sub_table)
                              {

                                if(data.Relation[j] == col_val_names_sub_table.trim())
                                {
                                    st = st + '<option value="'+data.Relation[j]+'">'+data.Relation[j]+'</option>';
                                }
                              }
                              else
                              {

                                st = st + '<option value="'+data.Relation[j]+'">'+data.Relation[j]+'</option>';
                              }

                          }
                          st = st + '</select></td>';

                      }
                      else if(inline_type == 'Calc')
                      {
                        st = st + '<td><input type="text" class="inlinetxt detailid_clc_clone_add_row form-control" id="'+data.Result[0].pk+'" disabled></td>';
                      }
                      else if(inline_type == 'File')
                      {
                        st = st + '<td><form method="POST" enctype="multipart/form-data" class="Inline_new_row_fileUploadForm_images_data_sub_table" name="'+ data.Result[0].nul_type +'"><input type="file" class="inlinetxt Inline_new_row_detailid_add_new_image_sub_table  form-control" name="files" id="'+data.Result[0].pk+'"></form></td>';
                      }
                      else
                      {
                          st = st + '<td><input type="'+inline_type+'" class="inlinetxt detailid_clone form-control" id="'+data.Result[0].pk+'" name="'+ data.Result[0].nul_type +'"></td>';

                      }
                  }
            });
        }
        st =  st + '<td><button class="cloned_row_add_sub_table btn btn-primary">Save</button></td><td><button class="cloned_row_add_sub_table_cancel btn btn-primary">Cancel</button></td>';
        st= st + '</tr>';
        console.log("ST IS : ");
        console.log(st);
        $(".table_body_additional").append(st);

    });


    $(document).on('click','.cloned_row_add_sub_table',function(){
        console.log("===== SAVING NEW ROW RECORDS =====")
        validation_checker = false;
        var values = $(".detailid_clone").map(function(){
                                                            if(($(this).val() == "" || $(this).val() == "Select..") && ($(this).attr('name') == "NOTNULL"))
                                                            {
                                                                $(this).css({'border':'1px solid #d1383d'});
                                                                validation_checker = true;
                                                            }
                                                            else
                                                            {
                                                                $(this).css({'border':'1px solid green'});
                                                            }
                                                            return $(this).val();
                                                        }).get();

        $(".Inline_new_row_detailid_add_new_image_sub_table").map(function(){
                                                                                if($(this).val() == "" && $(this).closest('form').attr('name') == "NOTNULL")
                                                                                {
                                                                                    $(this).css({'border':'1px solid #d1383d'});
                                                                                    validation_checker = true;
                                                                                }
                                                                                else
                                                                                {
                                                                                    $(this).css({'border':'1px solid green'});
                                                                                }
                                                                            }).get();

        var relation = $(".detailid_clone").map(function(){return $(this).attr('id');}).get();
        var mx = $(".sub_tables_main").attr('id');
        var table_id = sub_table_genaric_id;
        var imp = 0;
        var for_counter = 0;
        if(values.length % 2 != 0)
        {
            for_counter = (values.length + 1) / 2;
        }
        else
        {
            for_counter = values.length/2;
        }

        console.log("values initial : " + values);
        console.log("relation initial : " + relation);
        console.log('Table id : ' + table_id);
        console.log('Row Maximum id : ' + mx);
        console.log("for_counter : " + for_counter);

        if(validation_checker != true)
        {
            for(i=0; i<values.length; i++)
            {
                if (i == values.length - 1)
                {
                    imp = 1;
                }
                console.log("IMP : " + imp);
                console.log("values[i] : " + values[i]);
                $.ajax({
                    type:"POST",
                    url: "/adddetails",
                    async:false,
                    data:{csrfmiddlewaretoken: window.CSRF_TOKEN, d1: values[i], rr:relation[i], mx:mx , table_id:table_id, imp:imp},
                    success: function( data ){
                        console.log(data);
                    }
                });
            }
            /** UPDATING **/

           /** Image data upload **/
           console.log("--- Uploading Images ---")
           var image_columns_id = $(".Inline_new_row_detailid_add_new_image_sub_table").map(function(){return $(this).attr('id');}).get();
           var form_data_image = $(".Inline_new_row_fileUploadForm_images_data_sub_table").map(function(){return $(this)[0];}).get();
           console.log("image_columns_id : - ");
           console.log(image_columns_id);
           console.log("form_data_image : -");
           console.log(form_data_image);
           for(i=0; i<image_columns_id.length; i++)
           {
                var form = form_data_image[i];
                var data = new FormData(form);
                data.append("id", sub_table_genaric_id);
                data.append('max_row', $(".sub_tables_main").attr('id'));
                data.append('image_columns_id', image_columns_id[i]);
                data.append('csrfmiddlewaretoken', window.CSRF_TOKEN);
                $.ajax({
                    type:"POST",
                    enctype: 'multipart/form-data',
                    url: "/data_image_upload",
                    async:false,
                    data:data,
                    processData: false,
                    contentType: false,
                    cache: false,
                    timeout: 600000,
                    success: function( data ){
                      console.log(data);
                    }
                });
           }
           /** Image data upload end **/

            console.log("======== Add Detaild Calc Value ========")
            var relation_clc_tmp = $(".detailid_clc_clone_add_row").map(function(){return $(this).attr('id');}).get();
            var relation_clc = removeDuplicate(relation_clc_tmp);
            console.log("calc IDS : " + relation_clc);
            for(i=0; i<relation_clc.length; i++)
            {
                $.ajax({
                    type:"POST",
                    url: "/cal_add_details",
                    async:false,
                    data:{csrfmiddlewaretoken: window.CSRF_TOKEN, mx:mx, base_id:event.target.id, relation_clc:relation_clc[i], d1: values, rr:relation},
                    success: function( data ){
                      console.log(data);
                    }
                });
            }

            loading_tables();
        }
        else
        {
            new Noty({
               type: 'error',
               layout: 'topRight',
               theme: 'metroui',
               text: 'Required fields cannot be empty. ! 🤖',
               timeout: '4000',
               progressBar: true,
               closeWith: ['click'],
               killer: true,

            }).show();
        }



         /*
         $('.table_body_additional tr:last').remove();

         var st ='<tr>';

         for(i =0; i<values.length; i++)
         {
            st = st + '<td class="sub_td">' + values[i] + '</td>';
         }
         st = st +  '<td><button class="btn btn-sm btn-danger sub_table_row_delete">Delete</button></td>';
         st = st +  '<td><button class="btn btn-sm btn-danger sub_table_row_edite">Edit</button></td>';

         st = st + '</tr>';
         $(".table_body_additional").append(st);
         */
    });

    $(document).on('click','.cloned_row_add_sub_table_cancel',function(){
        $('.table_body_additional tr:last').remove();
    });

    $(document).on('click','.sub_table_new_column',function(){
        check_sub_table_or_main = 1;
    });

    $(document).on('click','.sub_table_new_ref_column',function(){
        check_sub_table_or_main = 1;
        key = sub_table_genaric_id;
        console.log('Mater table id : '+ key);
        $.ajax({
            url: '/relation_maters',
            type: 'POST',
            data: {csrfmiddlewaretoken: window.CSRF_TOKEN, key:key},
            success: function (data)
            {
              console.log(data);
              console.log(data.Result.length);
              $("#master_table_relation_select").empty()
              $("#master_table_relation_select").append('<option value="0">Select...</option>');
              for(i=0; i<data.Result.length; i++)
              {
                if(data.Result[i].pk != key){
                console.log(data.Result[i]);
                $("#master_table_relation_select").append('<option value="'+data.Result[i].pk+'">'+data.Result[i].base_name+'</option>')
              }
              }
            },
            error:function(e)
            {
              console.log(e)
            }
        });
        $("#Relation_column_model").modal('show');
    });



    /* SUB TABLE CALCULATION COLUMN CREATION MODEL OPENING */
    $(document).on('click','.sub_table_calcuation',function(){
        console.log("LOADING COLUMNS FOR CALCULATION...")
        var pkp = sub_table_genaric_id;
        console.log('pkp : ' + pkp);
        $(".column_box").empty();
        $(".equation_box").empty()
        $(".calc_result_column").val('');
        $.ajax({
            url: '/calculation_page',
            type: 'POST',
            data:{csrfmiddlewaretoken: window.CSRF_TOKEN, pkp:pkp},
            success:function(data){
                console.log(data.Result[0]['pk']);
                for(i=0; i<data.Result.length; i++)
                {
                    var colors = ['btn-success', 'btn-warning', '#btn-info', 'btn-default', 'btn-primary', 'btn-danger'];
                    var random_color = colors[Math.floor(Math.random() * colors.length)];
                    $(".column_box").append('<button class="btn btn_col '+random_color+'" id="'+data.Result[i]['pk']+'">'+data.Result[i]['c_name']+'</button>')
                }
            }
        });
        check_sub_table_or_main = 1;
        $('#calc_model').modal('show');

    });
    /* SUB TABLE CALCULATION COLUMN CREATION MODEL OPENING END */

    $(document).on('click','.sub_tbl_col_edit',function(){
        check_sub_table_or_main = 1;
        $(".col_md_rn").attr('id', $(this).attr('id'));
        $(".col_md_rn").val($(this).attr('name'));
        $('#rmodal').modal('show');
    });

    $(document).on('click','.sub_tbl_col_delete',function(){
        $.ajax({
            url: '/deletecolumn',
            type: 'POST',
            async: false,
            data: {csrfmiddlewaretoken: window.CSRF_TOKEN, id: $(this).attr('id'), base_id: sub_table_genaric_id},
            success: function (res) {
            },
            error: function (err) {
              console.log(err);
            }
        });
        loading_tables();
    });

});

function removeDuplicate(data)
{
    return [...new Set(data)]
}

function loading_tables()
{
    var table_id = sub_table_genaric_id;
    console.log("table_id : " + table_id)
    console.log("col_val_names_sub_table : " + col_val_names_sub_table)
    console.log("col_val_id_sub_table + " + col_val_id_sub_table)
    console.log("sub_table_genaric_id : " + sub_table_genaric_id);

    $(".addcol_additional").empty();
    $(".table_body_additional").empty();
    $(".new_row_btn_div").empty();

    $.ajax({
        type:"POST",
        url: "/Tables",
        async: false,
        data:{csrfmiddlewaretoken: window.CSRF_TOKEN, table_id:table_id, col_val_names_sub_table:col_val_names_sub_table, col_val_id_sub_table:col_val_id_sub_table},
        success: function( data )
        {
            $(".sub_tables_main").attr('id', data.max_row);
            var append_var = "<tr>";
            console.log(data);
            for(i=0; i<data.Cols.length; i++)
            {
                append_var = append_var + '<th id="' + data.Cols[i]["pk"] + '">' + data.Cols[i]["c_name"] + ' <img src="../static/images/trash.png" class="sub_tbl_col_delete" id="' + data.Cols[i]["pk"] +  '"> <img src="../static/images/edit.png" class="sub_tbl_col_edit" name="'+ data.Cols[i]["c_name"] +'" id="'+ data.Cols[i]["pk"] +'"></th>';
            }
            append_var = append_var + "</tr>"
            $(".addcol_additional").append(append_var);

            var append_body = "";
            console.log("=====================");
            console.log(data.Cols.length);
            for(i=0; i<data.Details.length; i++)
            {
                console.log("=====================");
                if((i>0) && (i % data.Cols.length == 0))
                {
                    append_body = append_body +  '<td><button class="btn btn-sm btn-danger sub_table_row_delete" id="' + data.Details[i][2] + '">Delete</button></td>';
                    append_body = append_body +  '<td><button class="btn btn-sm btn-danger sub_table_row_edite" id="' + data.Details[i][2] + '">Edit</button></td>';

                    append_body = append_body + '</tr>';

                    append_body = append_body + '<tr>';
                }
                else if(i == 0)
                {
                    append_body = append_body + '<tr>';
                }

               if(data.Details[i][3] == 'Image')
                {

                    append_body = append_body + '<td id="' + data.Details[i][1] + '" class="sub_td"><img src="'+ data.Details[i][0] +'"class="td_image"></td>';
                }
                else
                {
                    append_body = append_body + '<td id="' + data.Details[i][1] + '" class="sub_td">' + data.Details[i][0] + '</td>';
                }

            }
            l = data.Cols.length - 1
            if(data.Details.length > 0)
            {
                append_body = append_body + '<td><button class="btn btn-sm btn-danger sub_table_row_delete" id="' + data.Details[l][2] + '">Delete</button></td>';
                append_body = append_body + '<td><button class="btn btn-sm btn-danger sub_table_row_edite" id="' + data.Details[l][2] + '">Edit</button></td></tr>';
            }

            $(".table_body_additional").append(append_body);
            if(data.Cols.length > 0)
            {
                $(".new_row_btn_div").append('<button class="btn btn-sm btn-danger new_row_add_sub_table">New Record</button>');
            }

            $(".new_row_btn_div").append('<button class="btn btn-sm btn-info sub_table_calcuation">Add Calc. column</button>');
            $(".new_row_btn_div").append('<button class="btn btn-sm btn-primary sub_table_new_column" data-toggle="modal" data-target="#myModal1">Add new column</button>');
            $(".new_row_btn_div").append('<button class="btn btn-sm btn-success sub_table_new_ref_column">Add Ref. column</button>');
            $(".new_row_btn_div").append('<button class="btn btn-sm btn-success sub_table_import"  data-toggle="modal" data-target="#importmod">Import</button>');

        }
    });
}
