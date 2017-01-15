
function get_all_basegoods() {
   return  $.ajax({ 
       type: "GET",
       dataType: "json",
       contentType: "application/json; charset=utf-8",
       url: "http://localhost:5000/basegoods",
   });
}

function get_all_producables() {
   return  $.ajax({ 
       type: "GET",
       dataType: "json",
       contentType: "application/json; charset=utf-8",
       url: "http://localhost:5000/producables",
   });
}

function get_buildqueue(user_id) {
   return  $.ajax({ 
       type: "GET",
       dataType: "json",
       contentType: "application/json; charset=utf-8",
       url: "http://localhost:5000/users/"+user_id+"/buildqueue",
   });
}

function get_blueprint(id) {
   return  $.ajax({ 
       type: "GET",
       dataType: "json",
       contentType: "application/json; charset=utf-8",
       url: "http://localhost:5000/producables/"+id+"/blueprint",
   });
}

function sell_basegood(id) {
   return  $.ajax({ 
       type: "PUT",
       dataType: "json",
       data: "{ \"action\": \"sell\"}",
       contentType: "application/json; charset=utf-8",
       url: "http://localhost:5000/basegoods/"+id,
   });
}

function sell_producable(id) {
   return  $.ajax({ 
       type: "PUT",
       dataType: "json",
       data: "{ \"action\": \"sell\"}",
       contentType: "application/json; charset=utf-8",
       url: "http://localhost:5000/producables/"+id,
   });
}

function buy_basegood(id) {
   return  $.ajax({ 
       type: "PUT",
       dataType: "json",
       data: "{ \"action\": \"buy\"}",
       contentType: "application/json; charset=utf-8",
       url: "http://localhost:5000/basegoods/"+id,
   });
}

function produce_producable(id) {
   return  $.ajax({ 
       type: "PUT",
       dataType: "json",
       data: "{ \"action\": \"produce\"}",
       contentType: "application/json; charset=utf-8",
       url: "http://localhost:5000/producables/"+id,
   });
}

function get_inventory(id) {
   return  $.ajax({ 
       type: "GET",
       dataType: "json",
       contentType: "application/json; charset=utf-8",
       url: "http://localhost:5000/users/"+id+"/inventory",
   });
}

function get_user_info(id) {
   return  $.ajax({ 
       type: "GET",
       dataType: "json",
       contentType: "application/json; charset=utf-8",
       url: "http://localhost:5000/users/"+id,
   });
}

function handle_user_info(id) { 
      $(function(){
          var promise = get_user_info(id);
          promise.success(function(output) {
              console.log(output);
              });
          promise.error(function(output) {
              var msg = $.parseJSON(output.responseText).message;
              alert(msg);
              });
      });
}

function handle_basegood_selling(id) { 
      $(function(){
          var promise = sell_basegood(id);
          promise.success(function(output) {
              // Trying to update the id here to have immdediate response to the click event.
              // can't get the value here.. why?
              var asd = $("#"+id+"_inv").val();
              console.log(output.message);
              });
          promise.error(function(output) {
              var msg = $.parseJSON(output.responseText).message;
              alert(msg);
              });
      });
}

function handle_producable_selling(id) { 
      $(function(){
          var promise = sell_producable(id);
          promise.success(function(output) {
              // Trying to update the id here to have immdediate response to the click event.
              // can't get the value here.. why?
              var asd = $("#"+id+"_inv").val();
              console.log(output.message);
              });
          promise.error(function(output) {
              var msg = $.parseJSON(output.responseText).message;
              alert(msg);
              });
      });
}

function handle_basegood_buying(id) { 
      $(function(){
          var promise = buy_basegood(id);
          promise.success(function(output) {
              var inv_count = $("#1_price").val();
              console.log("inv lenght: " + inv_count)
              });
          promise.error(function(output) {
              var msg = $.parseJSON(output.responseText).message;
              alert(msg);
              });
      });
}

function handle_producable_production(id) { 
      $(function(){
          var promise = produce_producable(id);
          promise.success(function(output) {
              });
          promise.error(function(output) {
              var msg = $.parseJSON(output.responseText).message;
              alert(msg);
              });
      });
}

function init_struct() { 
      $(function(){
          var user_info = get_user_info(1)
          var basegoods = get_all_basegoods();
          var producables = get_all_producables();
          var inventory = get_inventory(1);
                
          var $progressbar = $('<div id=progressbar></div>')
          $('.container').append($progressbar);
          user_info.success(function(output) {
              var $header = $("<header id=header>"+output.user.name+":"+ output.user.balance+ "</header>");
              $('.container').append($header);
          });
          basegoods.success(function(output) {
              $.each(output.basegoods,function(index, item) {
                      var $div = $("<div>", {id: item.id, "class": "basegood", style:"max-width: 100px"});
                      $($div).append("<p>"+item.name + "</p>");
                      $($div).append("<p id="+item.id+"_price"+">$: "+item.price + "</p>");
                      inventory.success(function(output) {
                          // refactor
                          var len_inv=0;
                          $.map(output.inventory, function(inner_item, inner_index ) {
                              if(inner_item.basegood){
                                  if(inner_item.basegood.name == item.name) {
                                     len_inv++; 
                                  }
                              } else {
                                  if(inner_item.producable.name == item.name) {
                                     len_inv++;
                                  }
                              }
                         });
                         $($div).append("<p id="+item.id+"_inv"+">#: "+len_inv+ "</p>");
                      });
                      $($div).append("<button id=buy_basegood_btn"+item.id+" type=button>"+"buy"+"</button>");
                      $($div).append("<button id=sell_basegood_btn"+item.id+" type=button>"+"sell"+"</button>");
                      $('.basegood_container').append($div);
                      $($div).draggable();
                      $("#buy_basegood_btn"+item.id).on("click", function() {
                          handle_basegood_buying(item.id);
                      });
                      $("#sell_basegood_btn"+item.id).on("click", function() {
                          handle_basegood_selling(item.id);
                      });
                  });
              });
           basegoods.error(function(output) {
               console.log(output);
           });
          producables.success(function(output) {
              $.each(output.producables,function(index, item) {
                      var $div = $("<div>", {id: item.id, "class": "producable", style:"max-width: 100px"});
                      $($div).append("<p>"+item.name + "</p>");
                      var blueprint = get_blueprint(item.id);
                      blueprint.success(function(output) {
                          $.each(output.producable.basegoods, function(index, item) {
                              $($div).append("<p id="+item.id+"_blueprint"+">BP: "+item.name + "</p>");
                          });
                      });
                      $($div).append("<p id="+item.id+"_prod_price"+">$: "+item.price + "</p>");
                      inventory.success(function(output) {
                          // refactor
                          var len_inv=0;
                          $.map(output.inventory, function(inner_item, inner_index ) {
                              if(inner_item.basegood){
                                  if(inner_item.basegood.name == item.name) {
                                     len_inv++; 
                                  }
                              } else {
                                  if(inner_item.producable.name == item.name) {
                                     len_inv++;
                                  }
                              }
                         });
                         $($div).append("<p id="+item.id+"_prod_inv"+">#: "+len_inv+ "</p>");
                      });
                      $($div).append("<button id=sell_producable_btn"+item.id+" type=button>"+"sell"+"</button>");
                      $($div).append("<button id=produce_btn"+item.id+" type=button>"+"produce"+"</button>");
                      $('.producable_container').append($div);
                      $($div).draggable();
                      $("#produce_btn"+item.id).on("click", function() {
                          handle_producable_production(item.id);
                      });
                      $("#sell_producable_btn"+item.id).on("click", function() {
                          handle_producable_selling(item.id);
                      });
                  });
              });
           producables.error(function(output) {
               console.log(output);
           });
      });
}

    
setInterval("update_content();",5000);
function update_content(){
      var user_info = get_user_info(1)
      var basegood = get_all_basegoods();
      var producable = get_all_producables();
      var inventory = get_inventory(1);
      user_info.success(function(output) {
          $('#header').text(output.user.name+":"+output.user.balance);
      });
      basegood.success(function(output) {
          $.each( output.basegoods,function(index, item) {
                  $('#'+item.id+"_price").text("$: "+item.price)
                  inventory.success(function(output) {
                      // refactor  
                      var len_inv=0;
                      $.map(output.inventory, function(inner_item, inner_index ) {
                          if(inner_item.basegood){
                              if(inner_item.basegood.name == item.name) {
                                 len_inv++; 
                              }
                          } else {
                              if(inner_item.producable.name == item.name) {
                                 len_inv++;
                              }
                          }
                     });
                     $('#'+item.id+'_inv').text("#: "+len_inv);
                  });
              });
          });
       basegood.error(function(output) {
           console.log(output)
       });
      producable.success(function(output) {
          $.each( output.producables,function(index, item) {
                  $('#'+item.id+"_prod_price").text("$: "+item.price)
                  inventory.success(function(output) {
                      // refactor  
                      var len_inv=0;
                      $.map(output.inventory, function(inner_item, inner_index ) {
                          if(inner_item.basegood){
                              if(inner_item.basegood.name == item.name) {
                                 len_inv++; 
                              }
                          } else {
                              if(inner_item.producable.name == item.name) {
                                 len_inv++;
                              }
                          }
                     });
                     $('#'+item.id+'_prod_inv').text("#: "+len_inv);
                  });
              });
          });
       producable.error(function(output) {
           console.log(output)
       });
}
document.body.onload = init_struct;
