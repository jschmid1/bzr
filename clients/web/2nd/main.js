function get_all_basegoods() {
    return  $.ajax({
        type: "GET",
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        url: "http://localhost:5000/basegoods"
    });
}

function get_all_producables() {
    return  $.ajax({
        type: "GET",
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        url: "http://localhost:5000/producables"
    });
}

function get_buildqueue(user_id) {
    return  $.ajax({
        type: "GET",
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        url: "http://localhost:5000/users/"+user_id+"/buildqueue"
    });
}


function get_buildqueue_for(user_id, producable_id) {
    return  $.ajax({
        type: "GET",
        dataType: "json",
        async: false,
        contentType: "application/json; charset=utf-8",
        url: "http://localhost:5000/users/"+user_id+"/buildqueue/producable/"+producable_id
    });
}

function get_blueprint(id) {
    return  $.ajax({
        type: "GET",
        dataType: "json",
        async: false,
        contentType: "application/json; charset=utf-8",
        url: "http://localhost:5000/producables/"+id+"/blueprint"
    });
}

function sell_basegood(id) {
    return  $.ajax({
        type: "PUT",
        dataType: "json",
        data: "{ \"action\": \"sell\"}",
        contentType: "application/json; charset=utf-8",
        url: "http://localhost:5000/basegoods/"+id
    });
}

function sell_producable(id) {
    return  $.ajax({
        type: "PUT",
        dataType: "json",
        data: "{ \"action\": \"sell\"}",
        contentType: "application/json; charset=utf-8",
        url: "http://localhost:5000/producables/"+id
    });
}

function buy_basegood(id) {
    return  $.ajax({
        type: "PUT",
        dataType: "json",
        data: "{ \"action\": \"buy\"}",
        contentType: "application/json; charset=utf-8",
        url: "http://localhost:5000/basegoods/"+id
    });
}

function produce_producable(id) {
    return  $.ajax({
        type: "PUT",
        dataType: "json",
        data: "{ \"action\": \"produce\"}",
        contentType: "application/json; charset=utf-8",
        url: "http://localhost:5000/producables/"+id
    });
}

function get_inventory(id) {
    return  $.ajax({
        type: "GET",
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        url: "http://localhost:5000/users/"+id+"/inventory"
    });
}
function get_inventory_for_basegood(user_id, basegood_id) {
    return  $.ajax({
        type: "GET",
        dataType: "json",
        async: false,
        // how to handle it async?
        contentType: "application/json; charset=utf-8",
        url: "http://localhost:5000/users/"+user_id+"/inventory/basegood/"+basegood_id
    });
}

function get_inventory_for_producable(user_id, producable_id) {
    return  $.ajax({
        type: "GET",
        dataType: "json",
        async: false,
        contentType: "application/json; charset=utf-8",
        url: "http://localhost:5000/users/"+user_id+"/inventory/producable/"+producable_id
    });
}

function get_user_info(id) {
    return  $.ajax({
        type: "GET",
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        url: "http://localhost:5000/users/"+id
    });
}

function handle_basegood_selling(id) {
    $(function(){
        var promise = sell_basegood(id);
        promise.done(function(output) {
            var inv_len = $("#base_inv_"+id).text();
            $("#base_inv_"+id).html(parseInt(inv_len)-1)
        });
        promise.fail(function(output) {
            var msg = output.responseText;
            var html = $.templates("#alert").render(JSON.parse(msg));
            console.log(html)
            $('#container').append(html);
        });
    });
}

function handle_producable_selling(id) {
    $(function(){
        var promise = sell_producable(id);
        promise.done(function(output) {
            var inv_count = $("#prod_inv_"+id).text();
            $("#prod_inv_"+id).html(parseInt(inv_count)-1)
        });
        promise.fail(function(output) {
            var msg = output.responseText;
            console.log(output)
            var html = $.templates("#alert").render(JSON.parse(msg));
            $('#container').append(html);
        });
    });
}

function handle_basegood_buying(id) {
    $(function(){
        var promise = buy_basegood(id);
        promise.done(function(output) {
            var inv_count = $("#base_inv_"+id).text();
            $("#base_inv_"+id).html(parseInt(inv_count)+1)
        });
        promise.fail(function(output) {
            var msg = output.responseText
            console.log(msg);
            var html = $.templates("#alert").render(JSON.parse(msg));
            $('#container').append(html);
        });
    });
}

function handle_producable_production(id) {
    $(function(){
        var promise = produce_producable(id);
        promise.done(function(output) {
            var bqcnt = $("#inqueue_"+id).text();
            $("#inqueue_"+id).html(parseInt(bqcnt)+1)
            // missing the unique identifier here..
            progress(id, 3, output.producable.time); //jquery pseudo selector :last oder so
            var html = $.templates("#success").render({message: "Enqueued "+output.producable.name});
            $('#container').append(html);
            
        });
        promise.fail(function(output) {
            var msg = output.responseText;
            var html = $.templates("#alert").render(JSON.parse(msg));
            $('#container').append(html);
        });
    });
}

function round_to(dec, number) {
    return (Math.round(number * 100)/100).toFixed(dec);
}

function progress(itemid, bqid, duration) {
    var sel = $("#pr_"+itemid+"_"+bqid)
    sel.animate({ width: "100%" }, {queue: false, duration: (duration*3600), complete: function() { sel.parent().remove(); }});
}

function init_struct() {
    $(function(){
        var user_info = get_user_info(1);
        var basegoods = get_all_basegoods();
        var producables = get_all_producables();

        var buildqueue = get_buildqueue(1);

        user_info.done(function(output) {
            output.user.balance = round_to(2, output.user.balance);
            var html = $.templates("#header").render(output.user);
            $('#container').append(html);
        });
        basegoods.done(function(output) {
            $.each(output.basegoods,function(index, item) {
                get_inventory_for_basegood(1, item.id).done(function(output) {
                    item.ammount = output.ammount
                });
                item.price = round_to(2, item.price);
                var html = $.templates("#basegood").render(item);
                $("#container").append(html);
                $("#buy_basegood_btn_"+item.id).on("click", function() {
                    handle_basegood_buying(item.id);
                });
                $("#sell_basegood_btn_"+item.id).on("click", function() {
                    handle_basegood_selling(item.id);
                });
                $('#basegood_'+item.id).draggable()
            });
        });
        basegoods.fail(function(output) {
            console.log(output);
        });
        producables.done(function(output) {
            $.each(output.producables,function(index, item) {
                get_buildqueue_for(1, item.id).done(function(output) {
                    item.buildqueuecount = output.ammount;
                    item.buildqueue = output.producable;
                });
                get_inventory_for_producable(1, item.id).done(function(output) {
                    item.ammount = output.ammount
                });
                item.blueprint = new Array();
                get_blueprint(item.id).done(function(output) {
                    $.each(output, function (key, value) {
                        item.blueprint.unshift({name: value.basegood.name, ammount: value.ammount})
                    });
                });
                item.price = round_to(2, item.price);


                var html = $.templates("#producable").render(item);
                $('#container').append(html);
                $("#produce_btn_"+item.id).on("click", function() {
                    handle_producable_production(item.id);
                });
                $("#sell_producable_btn_"+item.id).on("click", function() {
                    handle_producable_selling(item.id);
                });
                $('#producable_'+item.id).draggable()

                $.each(item.buildqueue, function(key, value) {
                    item.bqid = value.id;
                    if ($("[id^=pr_"+item.id+"]").length <= 1) {
                        if ($("#pr_"+item.id+"_"+value.id).length == 0) {
                            var html = $.templates("#buildqueue").render(item);
                            $('#producable_'+item.id).append(html);
                            //st = new Date(value.time_start)
                            st = new Date($.now())
                            en = new Date(value.time_done)
                            console.log(en-st) 
                            progress(item.id, value.id, ((en-st) / 100 / 60 / 60))
                        }
                    }
                });
            });
        });

        producables.fail(function(output) {
            console.log(output);
        });
        var content = {author: "jxs"}
        var html = $.templates("#footer").render(content);
        $('#container').append(html);
    });
}


setInterval("update_content();",5000);
function update_content(){
    var basegood = get_all_basegoods();
    var producable = get_all_producables();
    get_user_info(1).done(function(output) {
        $("#header").html("<h1>"+output.user.name + " - " + round_to(2,output.user.balance)+"</h1>");
    });
    basegood.done(function(output) {
        $.each( output.basegoods,function(index, item) {
            get_inventory_for_basegood(1, item.id).done(function(output) {
                item.ammount = output.ammount
            });
            $("#base_price"+item.id).text(round_to(2, item.price));
            $("#base_inv_"+item.id).text(item.ammount)
        });
    });
    basegood.fail(function(output) {
        console.log(output)
    });
    producable.done(function(output) {
        $.each( output.producables,function(index, item) {
            get_inventory_for_producable(1, item.id).done(function(output) {
                item.ammount = output.ammount
            });
            get_buildqueue_for(1, item.id).done(function(output) {
                item.buildqueuecount = output.ammount
                item.buildqueue = output.producable
            });
            $.each(item.buildqueue, function(key, value) {
                if ($("[id^=pr_"+item.id+"]").length <= 1) {
                    if (!($("#pr_"+item.id+"_"+value.id).length)) {
                        item.bqid = value.id;
                        var html = $.templates("#buildqueue").render(item);
                        $('#producable_'+item.id).append(html);
                        //st = new Date(value.time_start)
                        st = new Date($.now())
                        en = new Date(value.time_done)
                        progress(item.id, value.id, ((en-st) / 100 / 60 / 60 ))
                    }
                }
            });
            $("#prod_price_"+item.id).text(round_to(2,item.price));
            $("#prod_inv_"+item.id).text(item.ammount);
            $("#inqueue_"+item.id).text(item.buildqueuecount);
        });
    });
    producable.fail(function(output) {
        console.log(output)
    });
    $(".alert").delay(4000).slideUp(200, function() {
            $(this).alert('close');
    });
}
window.onload = init_struct;
