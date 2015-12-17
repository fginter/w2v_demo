$(function(){
	$('#nearestform').submit(function(e){
		$.ajax({
			url: '/nearest',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
			    var respdata=jQuery.parseJSON(response)
			    $('#result').html(respdata.tbl);
			},
			error: function(error){
				console.log(error);
			}
		});
	    e.preventDefault();
	});
});
