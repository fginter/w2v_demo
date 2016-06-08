//hooks a form frm and result div resdiv to ajax path path
function ahook(frm,resdiv,path) {
    console.log("running ahook",frm, resdiv,path);
    $(frm).submit(function(e){
	data={};
	data["form"]=$(frm).serializeArray();
	data["model_name"]=$('#model_select').val();
	$.ajax({
	    url: $APP_ROOT+path,
	    data: data,
	    type: 'POST',
	    success: function(response){
		var respdata=jQuery.parseJSON(response)
		$(resdiv).html(respdata.tbl);
	    },
	    error: function(error){
		console.log(error);
	    }
	});
	e.preventDefault();
    });
}

$(function() {
    $( ".autocomplete" ).autocomplete({
      source: function(request, response) {
                $.ajax({
                  url: $APP_ROOT+'/autocomplete',
                  dataType: "json",
                  data: {
                    term : request.term,
                    model_name : $('#model_select').val()
                  },
                  success: function(data) {
                    response(data);
                  }
                });
            },
      minLength: 2,
    });
});
  

//I have no idea why I need to do this...
$(function() {ahook('#nearestform','#nearestresult','/nearest');});
$(function() {ahook('#analogyform','#analogyresult','/analogy');});
$(function() {ahook('#similarityform','#similarityresult','/similarity');});



