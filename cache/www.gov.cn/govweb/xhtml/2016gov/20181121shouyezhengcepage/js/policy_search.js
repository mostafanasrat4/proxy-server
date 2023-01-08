(function ($) {
									
	$('.dys_policy_search').on('click','.left_search_ico', function () {
		
			$('.dys_policy_search .form-input').fadeIn();
			
			$(this).fadeOut();
			
	});
	
	$('.goEnter').on('click', function () {
		
			$(this).parent().parent().hide();
			
			$('.left_search_ico').fadeIn();
			
	});
	
	var $dysPolicySearchText=$('.dys_policy_search .form-input .form_text');
	
	$dysPolicySearchText.on('focus', function () {
		if ($(this).val()==='搜索关键字') {
			$(this).val('');
		} 
	});
	
	$dysPolicySearchText.on('blur', function () {
		if ($(this).val()==='') {
			$(this).val('搜索关键字');
		}
	});
	

	$dysPolicySearchText.keydown(function(){
		
			var lenth = $(this).val().length;
			
			if(lenth >= 0){
				
				$(this).siblings('.close').show();
				
			}
		}).blur(function(){
			
			var _this = $(this);
			
			setTimeout(function () {
				
			_this.siblings('.close').hide();
			
			}, 500);
			
		});
		
		$('.dys_policy_search .form-input .close').click(function(){
			
			$(this).siblings('.form_text').val('');
			
			$(this).hide();
			
		})

})(jQuery);