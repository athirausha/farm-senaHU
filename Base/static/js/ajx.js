$(document).ready(function(){
    calc_val = [];
    calc_id = [];
    calc_val_original = [];
    referance_col = [];
    referance_col_name = [];
    referance_table = [];
  
  
    console.log("========== Satrt ============")
  
    referance_table_1stpage(param="master_table_relation_select");
  
    /********** FETCHING TABLE FOR REFERENCE COLUMN UI *******/
    $("#referance_add_btn").click(function(){
        console.log("=== Rferance table fecth started ===")
        referance_table_1stpage(param="relation_select");
        console.log("=== Rferance table fecth completed ===")
    });
    /********** FETCHING TABLE FOR REFERENCE COLUMN UI END *******/
  
    /********* Relation column of tables fetching **********/
    $(document).on('change','#master_table_relation_select',function(){
      fk = $("#master_table_relation_select").val();
      column_ftch(fk=fk, appendtoselct="master_table_relation_column_select")
    });
  
    $(document).on('change','#relation_select',function(){
      fk = $("#relation_select").val();
      column_ftch(fk=fk, appendtoselct="column_select")
    });
    /********** Relation column of tables fetching  end **********/
  
    $(document.body).on('change','#table_create_size',function(){
          if( ($(this).val() == "Date") || ($(this).val() == "Time") || ($(this).val() == "Image") )
          {
              $(this).closest('td').next('td').find('input').val(0);
              $(this).closest('td').next('td').find('input').prop('disabled', true);
          }
          else
          {
              $(this).closest('td').next('td').find('input').val('');
              $(this).closest('td').next('td').find('input').prop('disabled', false);
          }
    });
  
  
  
    $("#refrance_model_save").click(function(){
      referance_col.push($("#column_select").val());
      referance_col_name.push($("#relation_select option:selected").text());
      referance_table.push($("#relation_select").val());
      $('#newrefcol').modal('hide');
    });
  
  
    $(".baseform").click(function(event){
      /*************** CREATING MASTER TABLE  ***************/
      var new_tbl_id = 0;
      var new_tbl_name = '';
      console.log("new table id : " + new_tbl_id);
      var bname = $("#bname").val();
      var tname = $("#tname").val();
      var table_type = $("#table_type").val();
      var table_discription = $("#table_discription").val();
      var table_purpose = $("#table_purpose").val();
      var table_bcp = $("#table_bcp").val();
      var tags = $("#tags").val();
  
      // if( bname == '' || tname == '' || table_type == '' || table_discription == '' || table_purpose == '' || table_bcp == '' || tags == '')
      if( bname == '')
        {
            $.notify(
                {
              //   title: "<strong>Error : </strong> ",
                message: "Please Enter Business Name",
  
  
                },
                {
  
                     type: 'danger'
  
                }
            );
        }
        else
        if( tname == '')
        {
            $.notify(
                {
              //   title: "<strong>Error : </strong> ",
                message: "Please Enter Technical Name",
  
  
                },
                {
  
                     type: 'danger'
  
                }
            );
        }
      else
      {
          $.ajax({
              type:"POST",
              url: '/basemater',
              data:{csrfmiddlewaretoken: window.CSRF_TOKEN, bname:bname, tname:tname, table_type:table_type, table_discription:table_discription, table_purpose:table_purpose, table_bcp:table_bcp, tags:tags},
              async: false,
              success: function(data)
              {
                  console.log(data);
                  console.log(data.Status);
                  console.log(data.Id);
                  console.log(data.Name);
                  new_tbl_id = data.Id;
                  new_tbl_name = data.Name;
              }
          });
          /*************** CREATING MASTER TABLE END ***************/
  
          console.log("New table id : " + new_tbl_id);
  
          /*************** CREATING COLUMNS ***************/
          var col_siz=[];
          var values = $("input[name='baycol_add']").map(function(){return $(this).val();}).get();
          var tname = $("input[name='tech_name']").map(function(){return $(this).val();}).get();
          var d_type = $("select[name='coldatatype']").map(function(){return $(this).val();}).get();
           var null_v = $("select[name='noyes']").map(function(){return $(this).val();}).get();
          var col_siz = $("input[name='sizee']").map(function(){return $(this).val();}).get();
  
          fk= $("#bname").val();
          console.log("COLUMNS : "+values.length);
          console.log("DATA TYPE : "+d_type.length);
          console.log("col size : "+col_siz);
          if(values.length >=1 && d_type.length >=1 && tname.length >=1 && values[0]!= "")
          {
              for(i =0; i<values.length; i++)
                {
                  colname = values[i];
                  type_d = d_type[i];
                  tech_namee= tname[i];
                  col_sizee= col_siz[i];
                  v_null = null_v[i];
                  console.log('Column Name : '+colname);
                  console.log('Column Type : '+type_d);
                  console.log("col size : "+col_sizee);
                  console.log("Fk : "+ fk);
                  $.ajax({
                    type:"POST",
                    url: "/addcolumns",
                    data:{csrfmiddlewaretoken: window.CSRF_TOKEN, colname:colname,tech_namee:tech_namee, fk:fk, type_d:type_d,col_size:col_sizee,v_null:v_null},
                    async: false,
                    success: function( data )
                    {
                      console.log(data);
                    }
                  });
                }
            }
          else
          {
              $.notify(
                  {
                  title: "<strong>Warning : </strong> ",
                  message: "Please Enter Atleast A Row"
                  },
                  {
                       type: 'warning'
                  }
              );
          }
          /*************** CREATING COLUMNS END ***************/
  
      }
  
  
        /*************** ADDING REFERANCE COLUMN ***************/
        key = $("#master_table_relation_column_select").val();
        m_key =  $("#bname").val()
        name = $("#master_table_relation_select option:selected").text();
        if(key != 0)
        {
           console.log("1st row key : "+ key);
           console.log("1st m_key : " + m_key);
           $.ajax({
              url: '/save_relation_column_page_one',
              type: 'POST',
              async: false,
              data: {csrfmiddlewaretoken: window.CSRF_TOKEN, key:key, m_key:m_key, name:name},
              success: function (data)
              {
                  console.log(data);
              },
              error:function(e){ console.log(e) }
            });
        }
        if(referance_col.length > 0){
          console.log("2nd row key : "+referance_col);
          console.log("2nd row m_key : "+referance_table);
          console.log("2nd row name : "+referance_col_name)
          for(i=0; i<referance_col.length; i++)
          {
              key = referance_col[i];
              m_key = $("#bname").val();
              name = referance_col_name[i];
              $.ajax({
                  url: '/save_relation_column_page_one',
                  type: 'POST',
                  async: false,
                  data: {csrfmiddlewaretoken: window.CSRF_TOKEN, key:key, m_key:m_key, name:name},
                  success: function (data)
                  {
                      console.log(data);
                  },
                  error:function(e){ console.log(e) }
              });
          }
        }
        /*************** ADDING REFERANCE COLUMN END ***************/
  
  
  
      $("#custom-alert-box").append('<div class="alert alert-success alert-dismissible fade show" role="alert"><h4 class="alert-heading">Well done!</h4><p><strong>' + new_tbl_name + '</strong> model   created successfully!!!</p><hr><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>');
      $("#yourbusiness").append('<li><a class="nav-item" href="/viewbase/'+new_tbl_id+'"><i class="fa fa-window-maximize" aria-hidden="true"></i><p>'+new_tbl_name+'</p></a></li>');
  
  
    });
    /* .baseform click end */
  
  
  
      $("#btn_new_row").click(function(){
          var ref_ids = $(".ref_select_drop").map(function(){return $(this).attr('id');}).get();
          console.log("Ref IDS : "+ref_ids)
          $(".select_liner_data").empty();
          for(i=0; i < ref_ids.length; i++)
          {
              $.ajax({
                url: '/referanfce_col_filter',
                type: 'POST',
                async:false,
                data: {csrfmiddlewaretoken: window.CSRF_TOKEN, col_id:ref_ids[i]},
                success: function (data)
                {
                  console.log("Data form referanfce_col_filter : ");
                  console.log(data.filter_value);
                  for(x=0 ; x<data.filter_value.length; x++)
                  {
                    $("."+ref_ids[i]).append('<option value="'+data.filter_value[x].c_v+'" name="'+ data.filter_value[x].row_num +'">'+data.filter_value[x].c_v+'</option>')
                  }
                }
              });
          }
      });
  
      /**** LOAD COLUMNS FOR CALCULATION MODAL *****/
      $("#btn_open_calc_modal").click(function(){
          console.log("LOADING COLUMNS FOR CALCULATION...")
          var pkp = $(".addcol").attr('id');
          console.log('pkp : '+pkp)
          $(".column_box").empty();
          $(".equation_box").empty()
          $(".calc_result_column").val('');
          $.ajax({
              url: '/calculation_page',
              type: 'POST',
              data:{csrfmiddlewaretoken: window.CSRF_TOKEN, pkp:pkp},
              success:function(data){
                  console.log(data);
  
                  for(i=0; i<data.Result.length; i++)
                  {
                      var colors = ['btn-success', 'btn-warning', '#btn-info', 'btn-default', 'btn-primary', 'btn-danger'];
                      var random_color = colors[Math.floor(Math.random() * colors.length)];
                      $(".column_box").append('<button class="btn btn_col '+random_color+'" id="'+data.Result[i]['pk']+'">'+data.Result[i]['c_name']+'</button>')
                  }
  
              },
              error:function(res){
              console.log(res)
              }
          });
      });
      /**** LOAD COLUMNS FOR CALCULATION MODAL END *****/
  
      /**** LOAD COLUMNS FOR EDIT CALCULATION MODAL *****/
      $("#btn_open_calc_modal_edit").click(function(){
          console.log("LOADING COLUMNS FOR EDIT CALCULATION...")
          calc_val.length = 0;
          calc_id.length = 0
          var pkp = $(".addcol").attr('id');
          console.log('pkp : ' + pkp)
          $(".column_box_edit").empty();
          $(".equation_box_edit").empty()
          $(".calc_result_column_edit").val('');
          $.ajax({
              url: '/calculation_page',
              type: 'POST',
              data:{csrfmiddlewaretoken: window.CSRF_TOKEN, pkp:pkp},
              success:function(data){
                  console.log(data);
                  for(i=0; i<data.Result.length; i++)
                  {
                      var colors = ['btn-success', 'btn-warning', '#btn-info', 'btn-default', 'btn-primary', 'btn-danger'];
                      var random_color = colors[Math.floor(Math.random() * colors.length)];
                      $(".column_box_edit").append('<button class="btn btn_col '+random_color+'" id="'+data.Result[i]['pk']+'">'+data.Result[i]['c_name']+'</button>');
                  }
                  for(i=0; i<data.Calc.length; i++)
                  {
                      $(".edit_calc_col_name").append('<option value="'+data.Calc[i]['column_id']+'">'+data.Calc[i]['column_name']+'</option>');
                  }
              },
              error:function(res){
              console.log(res)
              }
          });
      });
      /**** LOAD COLUMNS FOR EDIT CALCULATION MODAL END *****/
  
      $(document).on('change','.edit_calc_col_name',function(){
          col_fk = $(".edit_calc_col_name").val();
          $.ajax({
              url: '/calc_equation_fetch',
              type: 'POST',
              data:{csrfmiddlewaretoken: window.CSRF_TOKEN, col_fk:col_fk},
              success:function(data){
                  console.log(data);
                  $(".calc_existing_column_name").val(data.col_name);
                  $(".calc_existing_column_equ").val(data.calc_equ);
                  $(".calc_existing_column_equ").attr('id', data.calc_id)
  
              }
          });
  
      });
  
  
  
      var sequence_number = 1
      /* ADDING COLUMN TO EQUATION */
      $(document).on('click','.column_box > .btn_col',function(event){
          var tag = $(this).clone().attr({"name":sequence_number})
  
          $(".equation_box").append(tag);
          calc_val.push($(this).text());
          calc_val_original.push($(this).text());
          calc_id.push($(this).attr('id'));
      });
      /* ADDING COLUMN TO EQUATION END */
  
      /* ADDING COLUMN TO EQUATION -  IN EDIT CASE */
      $(document).on('click','.column_box_edit > .btn_col',function(event){
          var tag = $(this).clone().attr({"name":sequence_number})
  
          $(".equation_box_edit").append(tag);
          calc_val.push($(this).text());
          calc_val_original.push($(this).text());
          calc_id.push($(this).attr('id'));
      });
      /* ADDING COLUMN TO EQUATION - IN EDIT CASE END */
  
      /** ADDING OPERATOR FROM OPERATOR BOX TO EQUATION BOX AND ARRAY **/
      $(document).on('click','.operator_box > .btn-oprator',function(event){
          var tag = $(this).clone().attr({"name":sequence_number})
  
          $(".equation_box").append(tag);
          calc_val.push($(this).text());
          calc_val_original.push($(this).text());
          calc_id.push($(this).attr('id'));
      });
      /** ADDING OPERATOR FROM OPERATOR BOX TO EQUATION BOX AND ARRAY END **/
  
      /** ADDING OPERATOR FROM OPERATOR BOX TO EQUATION BOX AND ARRAY - IN EDIT **/
      $(document).on('click','.operator_box_edit > .btn-oprator',function(event){
          var tag = $(this).clone().attr({"name":sequence_number})
  
          $(".equation_box_edit").append(tag);
          calc_val.push($(this).text());
          calc_val_original.push($(this).text());
          calc_id.push($(this).attr('id'));
      });
      /** ADDING OPERATOR FROM OPERATOR BOX TO EQUATION BOX AND ARRAY END - IN EDIT **/
  
  
      /** ADDING () FROM OPERATOR BOX TO EQUATION BOX  **/
      $(document).on('click','.operator_box > .btn-bracket',function(event){
          var tag = $(this).clone().attr({"name":sequence_number});
          $(".equation_box").append(tag);
          calc_val_original.push($(this).text());
      });
      /** ADDING () FROM OPERATOR BOX TO EQUATION BOX END **/
  
      /** ADDING () FROM OPERATOR BOX TO EQUATION BOX - IN EDIT CASE  **/
      $(document).on('click','.operator_box_edit > .btn-bracket',function(event){
          var tag = $(this).clone().attr({"name":sequence_number});
          $(".equation_box_edit").append(tag);
          calc_val_original.push($(this).text());
      });
      /** ADDING () FROM OPERATOR BOX TO EQUATION BOX END - IN EDIT CASE **/
  
      /*** REMOVE COLUMNS FROM EQUATION BOX ****/
      $(document).on('click','.equation_box > .btn_col',function(event){
          $(this).remove();
      });
      /*** REMOVE COLUMNS FROM EQUATION BOX END ****/
  
      /*** REMOVE COLUMNS FROM EQUATION BOX  - IN EDIT CASE ****/
      $(document).on('click','.equation_box_edit > .btn_col',function(event){
          $(this).remove();
      });
      /*** REMOVE COLUMNS FROM EQUATION BOX END - IN EDIT CASE ****/
  
      /*** REMOVE OPERATOR FROM EQUATION BOX ****/
      $(document).on('click','.equation_box > .btn-oprator',function(event){
          $(this).remove();
      });
      /*** REMOVE OPERATOR FROM EQUATION BOX END ****/
  
      /*** REMOVE OPERATOR FROM EQUATION BOX - IN EDIT CASE ****/
      $(document).on('click','.equation_box_edit > .btn-oprator',function(event){
          $(this).remove();
      });
      /*** REMOVE OPERATOR FROM EQUATION BOX END - IN EDIT CASE ****/
  
      /*** REMOVE BRACKET FROM EQUATION BOX ****/
      $(document).on('click','.equation_box > .btn-bracket',function(event){
          $(this).remove();
      });
      /*** REMOVE BRACKET FROM EQUATION BOX END ****/
  
      /*** REMOVE BRACKET FROM EQUATION BOX - IN EDIT CASE ****/
      $(document).on('click','.equation_box_edit > .btn-bracket',function(event){
          $(this).remove();
      });
      /*** REMOVE BRACKET FROM EQUATION BOX END - IN EDIT CASE ****/
  
      /**** ADDING CONSTANT VALUE BUTTON TO OPERATOR DIV ****/
      $("#adding_const_btn").click(function(){
          var vl_s = $("#cr_sv").val();
          $(".operator_box").append('<button class="btn btn-success btn-oprator" id="const">'+vl_s+'</button>');
      });
      /**** ADDING CONSTANT VALUE BUTTON TO OPERATOR DIV END ****/
  
      /**** ADDING CONSTANT VALUE BUTTON TO OPERATOR DIV - IN EDIT ****/
      $("#adding_const_btn_edit").click(function(){
          var vl_s = $("#cr_sv_edit").val();
          $(".operator_box_edit").append('<button class="btn btn-success btn-oprator" id="const">'+vl_s+'</button>');
      });
      /**** ADDING CONSTANT VALUE BUTTON TO OPERATOR DIV END - IN EDIT ****/
  
      /**** UPDATING CALCULATION EQUATION  *****/
      $(".update_calc").click(function(){
          var rs_column  = $(".calc_result_column_edit").val();
          var column_id = $(".edit_calc_col_name").val();
          var calc_pk =  $(".calc_existing_column_equ").attr('id');
          var original_col_name = $(".calc_existing_column_name").val();
          var base_id = $("thead").attr('id');
  
          console.log("Result Column : " + rs_column);
          console.log("Original_col_name : " + original_col_name);
          console.log("Column Id : " + column_id);
          console.log("Calc pk : " + calc_pk);
          console.log("Calc_val : " + calc_val);
          console.log("Calc_id : " + calc_id);
          console.log("Calc_val_original : " + calc_val_original);
  
          $.ajax({
              url: '/calc_edit',
              type: 'POST',
              async: false,
              data:{csrfmiddlewaretoken: window.CSRF_TOKEN, rs_column:rs_column, column_id:column_id, calc_pk:calc_pk, original_col_name:original_col_name, calc_val:calc_val, calc_id:calc_id, calc_val_original:calc_val_original, base_id:base_id},
              success:function(data){
                  console.log(data);
              },
              error:function(res){
              console.log(res)
              }
          });
           setTimeout(function(){
              location.reload();
            }, 500);
      });
  
  
      /**** SAVE CALCULATION EQUATION  *****/
      $(".save_calc").click(function(){
          var rs_column  = $(".calc_result_column").val();
          var fk = 0;
          var mx = 0;
          if(check_sub_table_or_main == 1)
          {
              fk = sub_table_genaric_id;
              mx = $(".sub_tables_main").attr('id');
          }
          else
          {
              fk = $(".addcol").attr('id');
              mx = $(".table_body").attr('id');
          }
  
  
          console.log("Resultant column name : "+rs_column)
          console.log("Values From calculation result box : ");
          console.log(calc_val);
          console.log("ids From calculation result box : ");
          console.log(calc_id);
          console.log('Row Maximum id : '+mx);
          console.log('FK is : '+ fk)
  
          $.ajax({
              url: '/calc_save',
              type: 'POST',
              async: false,
              data:{csrfmiddlewaretoken: window.CSRF_TOKEN, arr_val:calc_val, arr_ids:calc_id, rs_column:rs_column, fk: fk, mx:mx},
              success:function(data){
                  console.log(data);
              },
              error:function(res){
              console.log(res)
              }
          });
  
          calc_val.length = 0;
          calc_id.length = 0;
          if(check_sub_table_or_main == 1)
          {
              $(".cal_sign_box").empty();
              var bts = '<button class="btn btn-info btn-oprator" id="+">+</button><button class="btn btn-primary btn-oprator" id="-">-</button><button class="btn btn-danger btn-oprator" id="*">*</button><button class="btn btn-warning btn-oprator" id="/">/</button><button class="btn btn-success btn-oprator" id="%">%</button><button class="btn btn-success btn-oprator" id=">">Max</button><button class="btn btn-success btn-oprator" id="<">Min</button> <button class="btn btn-success btn-bracket" id="(">(</button><button class="btn btn-success btn-bracket" id=")">)</button>'
              $(".cal_sign_box").append(bts);
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
  
                         append_body = append_body + '<td id="' + data.Details[i][1] + '" class="sub_td">' + data.Details[i][0] + '</td>';
  
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
  
                  }
               });
  
          }
          else
          {
              setTimeout(function(){location.reload();}, 2000);
          }
      });
      /**** SAVE CALCULATION EQUATION END *****/
  
  });
  
  
  function referance_table_1stpage(param)
  {
      $.ajax({
          url: '/relation_maters',
          type: 'POST',
          async: false,
          data: {csrfmiddlewaretoken: window.CSRF_TOKEN},
          success: function (data)
          {
              console.log(data);
              $("#"+param).empty();
              $("#"+param).append('<option value="0">Select...</option>');
              for(i=0; i<data.Result.length; i++)
              {
                $("#"+param).append('<option value="'+data.Result[i].pk+'">'+data.Result[i].base_name+'</option>')
              }
          },
          error:function(e)
          {
              console.log(e)
          }
      });
  }
  
  
  function column_ftch(fk, appendtoselct)
  {
      $.ajax({
          url: '/filter_columns_for_relation',
          type: 'POST',
          data: {csrfmiddlewaretoken: window.CSRF_TOKEN, fk},
          success: function (data)
          {
              console.log(data);
              $("#"+appendtoselct).empty()
              for(i=0; i<data.Result.length; i++)
              {
                  $("#"+appendtoselct).append('<option value="'+data.Result[i].pk+'">'+data.Result[i].c_name+'</option>')
              }
          },
          error:function(e){ console.log(e) }
      });
  }