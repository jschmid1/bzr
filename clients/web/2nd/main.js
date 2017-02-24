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
          promise.done(function(output) {
              console.log(output);
              });
          promise.fail(function(output) {
              var msg = output.responseText
              var html = $.templates("#alert").render(msg)
              $('#container').append(html);
              });
      });
}

function handle_basegood_selling(id) { 
      $(function(){
          var promise = sell_basegood(id);
          promise.done(function(output) {
              // Trying to update the id here to have immdediate response to the click event.
              // can't get the value here.. why?
              var asd = $("#"+id+"_inv").val();
              console.log(output.message);
              });
          promise.fail(function(output) {
              var msg = output.responseText
              var html = $.templates("#alert").render(msg)
              console.log(msg)
              console.log(html)
              $('#container').append(html);
              });
      });
}

function handle_producable_selling(id) { 
      $(function(){
          var promise = sell_producable(id);
          promise.done(function(output) {
              // Trying to update the id here to have immdediate response to the click event.
              // can't get the value here.. why?
              var asd = $("#"+id+"_inv").val();
              console.log(output.message);
              });
          promise.fail(function(output) {
              var msg = output.responseText
              var html = $.templates("#alert").render(msg)
              $('#container').append(html);
              });
      });
}

function handle_basegood_buying(id) { 
      $(function(){
          var promise = buy_basegood(id);
          promise.done(function(output) {
              var inv_count = $("#1_price").val();
              console.log("inv lenght: " + inv_count)
              });
          promise.fail(function(output) {
              var msg = output.responseText
              var html = $.templates("#alert").render(msg)
              $('#container').append(html);
              });
      });
}

function handle_producable_production(id) { 
      $(function(){
          var promise = produce_producable(id);
          promise.done(function(output) {
              progress($('#pr' + id), output.producable.time, id); //jquery pseudo selector :last oder so
              });
          promise.fail(function(output) {
              var msg = output.responseText
              var html = $.templates("#alert").render(msg)
              $('#container').append(html);
              alert(msg);
              });
      });
}

function round_to(dec, number) {
      return (Math.round(number * 100)/100).toFixed(dec);
}

function progress($element, duration, id) {
        console.log(duration)
        $element.animate({ width: "100%" }, {queue: false, duration: (duration*3600), complete: function() { $element.attr('style', "width: 0%"); }});
}

function init_struct() { 
      $(function(){
          var user_info = get_user_info(1)
          var basegoods = get_all_basegoods();
          var producables = get_all_producables();
          var inventory = get_inventory(1);
          user_info.done(function(output) {
              var html = $.templates("#header").render(output.user)
              $('#container').append(html);
          });
          basegoods.done(function(output) {
              $.each(output.basegoods,function(index, item) {
                      var len_inv=0;
                      // query inv and calculate how much of each basegood you have
                      inventory.done(function(output) {
                          // refactor
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
                      });
                      item.inv_len = len_inv
                      item.price = round_to(2, item.price)
                      var html = $.templates("#basegood").render(item)
                      $('#container').append(html);
                      $("#buy_basegood_btn"+item.id).on("click", function() {
                          handle_basegood_buying(item.id);
                      });
                      $("#sell_basegood_btn"+item.id).on("click", function() {
                          handle_basegood_selling(item.id);
                      });
                  });
              });
           basegoods.fail(function(output) {
               console.log(output);
           });

          producables.done(function(output) {
              $.each(output.producables,function(index, item) {
                      item.blueprints = [];
                      var blueprint = get_blueprint(item.id);
                      blueprint.done(function(output) {
                          var counts = {};
                          // map duplicates and create a Array of Basegood: Ammount
                          for (var i = 0; i < output.producable.length; i++) {
                              counts[output.producable[i].name] = 1 + (counts[output.producable[i].name] || 0);
                          };
                          // Remap to json conform format: name: value, ammount: value
                          new_map = {};
                          $.each(counts, function (key, value) {
                              item.blueprints.unshift({name: key, ammount: value})
                          });

                        
                      });
                      var len_inv=0;
                      // Calculate the inventory length.
                      inventory.done(function(output) {
                          // refactor
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
                      });
                      item.ammount = len_inv
                      item.price = round_to(2, item.price);
                      var html = $.templates("#producable").render(item)
                      $('#container').append(html);
                      $("#produce_btn"+item.id).on("click", function() {
                          handle_producable_production(item.id);
                      });
                      $("#sell_producable_btn"+item.id).on("click", function() {
                          handle_producable_selling(item.id);
                      });
                  });
              });
           producables.fail(function(output) {
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
      user_info.done(function(output) {
          var html = $.templates("#header").render(output.user)
          // how to update .. can i render and then replace?
          //$('#container').text(html);
      });
      basegood.done(function(output) {
          $.each( output.basegoods,function(index, item) {
                  $('#'+item.id+"_price").text("$: " + round_to(2, item.price))
                  inventory.done(function(output) {
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
       basegood.fail(function(output) {
           console.log(output)
       });
      producable.done(function(output) {
          $.each( output.producables,function(index, item) {
                  $('#'+item.id+"_prod_price").text("$: "+round_to(2,item.price))
                  inventory.done(function(output) {
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
       producable.fail(function(output) {
           console.log(output)
       });
}
window.onload = init_struct;
