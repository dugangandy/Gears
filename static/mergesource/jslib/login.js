var reg = /\s/g;
function validateUserName() {
	var userName = $('#userName').val();
	if ('' == userName || '' == userName.replace(reg, '')) {
		$('#userNameSpan').html('<img src="style/images/delete.gif" style="vertical-align:middle"/>用户名不能为空');
		// $('#userName').focus();
		return false;
	} else {
		$('#userNameSpan').html('');
		return true;
	}
}
function validatePassword() {
	var password = $('#password').val();
	if ('' == password) {
		$('#passwordSpan').html('<img src="style/images/delete.gif" style="vertical-align:middle"/>密码不能为空');
		// $('#password').focus();
		return false;
	} else {
		$('#passwordSpan').html('');
		return true;
	}
}

function login(){
	if(!validateUserName()) return false;
	if(!validatePassword()) return false;
	var userName = $('#userName').val();
	var password = $('#password').val();
	var url = "validateUserExists?userName=" + encodeURI(encodeURI(userName)) + "&&password=" + encodeURI(password);
	$('#subButton').attr({
		"disabled" : "disabled"
	});
	$.ajax({
		url : url,
		type : 'POST',
		dataType : 'json',
		error : function() {
			alert('通过用户名和密码验证用户出错啦!');
			setTimeout("$('#subButton').removeAttr('disabled')", 3000);
		},
		success : function(r) {
			if(!r.success){
				$('#userNameSpan').html('<img src="style/images/delete.gif" style="vertical-align:middle"/>错误的用户名或密码');
				setTimeout("$('#subButton').removeAttr('disabled')", 1000);
				return;
			}else{
				$('#userNameSpan').html('<img src="style/images/ok.gif" style="vertical-align:middle"/>登录成功');
				$('#subButton').attr({
					"disabled" : "disabled"
				});
				$('#loginForm').submit();
				return;
			}
		}
	});	
}