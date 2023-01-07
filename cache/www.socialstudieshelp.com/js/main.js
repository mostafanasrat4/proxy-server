function drop(list){
var listElementStyle=document.getElementById(list).style;
if (listElementStyle.display=="none"){
listElementStyle.display="block";}
else {
listElementStyle.display="none";
}
}



/***** BEGIN DROPDOWNS ******/

var agt = navigator.userAgent.toLowerCase();
	var is_major = parseInt(navigator.appVersion);
	var is_nav = ((agt.indexOf('mozilla') != -1) && (agt.indexOf('spoofer') == -1) && (agt.indexOf('compatible') == -1) && (agt.indexOf('opera') == -1) && (agt.indexOf('webtv') == -1));
	var is_nav4up = (is_nav && (is_major >= 4));
	var is_ie = (agt.indexOf("msie") != -1);
	var is_ie3  = (is_ie && (is_major < 4));
	var is_ie4  = (is_ie && (is_major == 4) && (agt.indexOf("msie 5") == -1) && (agt.indexOf("msie 6") == -1));
	var is_ie4up = (is_ie && (is_major >= 4));
	var is_ie5up  = (is_ie  && !is_ie3 && !is_ie4);
	var is_mac = (agt.indexOf("mac") != -1);
	var is_gecko = (agt.indexOf("gecko") != -1);

	function grabObject (id) {
		if (is_ie4) {
			var view = eval(id);
		}
		if (is_ie5up || is_gecko) {
			var view = document.getElementById(id);
		}
		return view;
	}

	function show_hide(id) {
		if(is_ie4up || is_gecko) {

			var hdn_div = grabObject('hdn'+id);
			var shdn_span = grabObject('shdn'+id);
			var xpand_img = grabObject('img'+id);
			if(hdn_div.style.display == 'block') {
				hdn_div.style.display = 'none';		
		//	document.getElementById(id).src= 'images/arrowdn.gif';
			} else {
				hdn_div.style.display = 'block';
		//	document.getElementById(id).src= 'images/arrowdn2.gif';
			}

		}
	}

	function open_div(number, default_status) {
		if (is_ie4up || is_gecko) {
			document.writeln("<div id='hdn" + number + "' name='hdn" + number + "' style='display: " + default_status + ";'>");
		}
	}

	function close_div(number, default_status) {
		if (is_ie4up || is_gecko) {
			document.writeln("</div>");
		}
	}
	
/***** END DROPDOWNS ******/
