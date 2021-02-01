// To connect and retrieve the tables in the Database
var allt;
var st=[];
var res=[];
function retrieveTables() {
  $('.inibut').show();
  //var url = 'http://localhost:5000/QBE/?query={all_tables(user_name:"'+$("#uid").val()+'",password:"'+$("#pid").val()+'",db_name:"'+$("#dname").val()+'")}';
  var url = 'http://localhost:5000/QBE/?query={alltables(username:"'+$("#uid").val()+'",password:"'+$("#pid").val()+'",dbname:"'+$("#dname").val()+'"){tablename}}';
  //console.log(url);
  $.ajax({
    url: url,
    type: 'GET',
    success: function(response) {
      allt = response.data.alltables;
      var htmlCode ="";
      for (var i=0; i<allt.length; i++)
        htmlCode += '<label for="'+allt[i].tablename+'">'+allt[i].tablename+'  </label>'+
                        '<select name="'+allt[i].tablename+'" id="'+allt[i].tablename+'">'+
                            '<option value="'+0+'">0</option>'+
                            '<option value="'+1+'">1</option>'+
                            '<option value="'+2+'">2</option>'+
                        '</select><br><br>';
      $("#total_tables").html(htmlCode);
    },
    error: function(error) {
      alert("ERROR");
      console.log(error);
    }
  });
}

//To get skeletons of the selected tables

function getSkeletons(){
  var i=0;
  st=[];
  for (i=0; i<allt.length; i++)
  {
    var j=parseInt($("#"+allt[i].tablename+" option:selected").text(),10)
    if(j!=0)
    {
      for(var k=0;k<j;k++)
      {
        st.push(allt[i].tablename+"_"+k);
        var url = 'http://localhost:5000/QBE/?query={tableAttributes(tablename:"'+allt[i].tablename+'",username:"'+$("#uid").val()+'",password:"'+$("#pid").val()+'",dbname:"'+$("#dname").val()+'"){attributeName}}';
        $.ajax({
          url: url,
          type: 'GET',
          indexValue: k,
          success: function(response) {
            var tattr = response.data.tableAttributes;
            var tname = tattr[0].attributeName;
            var htmlCode="<table class="+tname+"_"+this.indexValue+"><tr>";
            htmlCode += '<th class="bold_tbname">'+tattr[0].attributeName+'</th>';
            for (var c=1; c<tattr.length; c++)
              htmlCode += '<th>'+tattr[c].attributeName+'</th>';
            htmlCode+="</tr><tr>";
            for (var c=0; c<tattr.length; c++)
              htmlCode += '<td><input type="text" id="'+tname+"_"+this.indexValue+"_"+tattr[c].attributeName+'"></td>';
            htmlCode +='</tr></table><br><br>';
            $("#skeletons").append(htmlCode);
            $('.conbut').show();
          },
          error: function(error) {
            alert("ERROR");
            console.log(error);
          }
        });

      }
    }
  }
  $("#get_skeleton").prop('disabled',true);
  $("#get_skeleton").css("background-color","black");
}

//To reset Skeletons

function resetSkeletons(){
  $("#skeletons").html("");
  $("#get_skeleton").prop('disabled',false);
  $("#get_skeleton").css("background-color","#4CAF50");
  $(".conbut").hide();
  $("#results").html("");
  $('#query_space').html("");
}

//Query Results
function getResults(){
  columns=[]
    for(var i=0;i<st.length;i++)
    {
      $("table."+st[i]+" td").each(function()
      {
        var temp=$(this).find("input").val();
        if(temp=="")
          {
            temp="NULL";
          }
        columns.push(temp);
      });
    }
    var selectedTables=st.toString();
    var selectedColumns=columns.toString();
    var conditionBox=$("#condition_box").val();
    var url = 'http://localhost:5000/QBE/?query={Qres(username:"'+$("#uid").val()+'",password:"'+$("#pid").val()+'",dbname:"'+$("#dname").val()+'",sTables:"'+selectedTables+'",Columns:"'+selectedColumns+'",conditionBox:"'+conditionBox+'"){recValue querystr}}';
    $.ajax({
      url: url,
      type: 'GET',
      success: function(response) {
        res = response.data.Qres;
        //$("#results").html("<p>"+res+"</p>");
        var htmlCode="<table align='center'><tr>";
        for(var i=0;i<res.length;i++)
        {
          if(i==0)
          {
            var inner=res[i].recValue;
            var query=res[i].querystr;
            query=query+";";
            var test_code="<p align='center'>"+query+"</p>";
            $("#query_space").html(test_code);
            for(var j=0;j<inner.length;j++)
            {
              htmlCode+='<th>'+inner[j]+'</th>';
            }
            htmlCode+='</tr>';
          }
          else
          {
              htmlCode+='<tr>';
              var inner=res[i].recValue;
              for(var j=0;j<inner.length;j++)
              {
                htmlCode+='<td>'+inner[j]+'</td>';
              }
              htmlCode+='</tr>';
          }
        }
        $("#results").html(htmlCode);
      },
      error: function(error) {
        alert("ERROR");
        console.log(error);
      }
    });
}
