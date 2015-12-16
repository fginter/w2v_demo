$(function(){
	$('button').click(function(){
		var user = $('#txtUsername').val();
		var pass = $('#txtPassword').val();
		$.ajax({
			url: '/nearest',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
			    var respdata=jQuery.parseJSON(response)
			    $('#result').html(respdata.tbl);
			    $('#result').fadeIn('slow');
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});
