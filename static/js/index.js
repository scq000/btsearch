function search() {
	$('.tip').show();
	$.post('/query',{"keyword":$('.search').find('input').val()}, function(data, textStatus, xhr) {
		$('.tip').hide();
		if(data.code == 0){
			$('.result').find("table").empty();
			for(var i=0;i<data.rows.length;i++){
				$('.result').find("table").append('<tr><td><p>标题：'+ data.rows[i].title +'</p><p>磁力链：'+ data.rows[i].magnet +'</p><p>迅雷链接：'+ data.rows[i].thunder +'</p><p>大小：'+ data.rows[i].size +'</p></td></tr>');
			}
		}else{
			$('.result').find("table").empty();
			alert(data.msg);
		}
	},"json");
}

