/* ----------------------- 
 * $RCSfile: aware.js,v $
 * $Revision: 1.9 $ 
 * $Date: 2007-11-03 15:02:39 $ 
 * $Author: aps1 $ 
 * $Name: not supported by cvs2svn $ 
 * ----------------------- */


function updateForm() {
	document.forms[1].zoomdir.value = document.forms[0].zoomdir.value;
}

function redrawMap() {
	document.forms[0].submit();
}

function openWin(name, x, y) {
	window.open("", name, "toolbar=no,menubar=no,scrollbars=yes,height=" + y + ",width=" + x);
}

function print_date() {
		var d = new Date();
		document.write(d.toGMTString());
}


function doRefresh() {
	setInterval("document.forms[0].submit()", " . 1000 * $refresh . ");
}


function toggle_refresh(strURL) {

	var reload = document.getElementById("ajaxEnabled").value;

	if (reload == "yes") {
		document.getElementById("ajaxEnabledImg").src = "images/remove.png";
		document.getElementById("ajaxEnabled").value = "no";
		update_status("Auto-Update disabled");
	} else {
		document.getElementById("ajaxEnabledImg").src = "images/reload.png";
		document.getElementById("ajaxEnabled").value = "yes";
		xmlHttpPost(strURL);
	}

}

function xmlHttpPost(strURL) {


	var reload = document.getElementById("ajaxEnabled").value;

	if (reload == "no") {
		// update was disabled since this was scheduled
		return;
	}

	update_status("Requesting update...");

	var xmlHttpReq = false;
	var self = this;
	if (window.XMLHttpRequest) {
		self.xmlHttpReq = new XMLHttpRequest();
	} else if (window.ActiveXObject) {
		self.xmlHttpReq = new ActiveXObject("Microsoft.XMLHTTP");
	}


	try {
		self.xmlHttpReq.open('POST', strURL, true);
		self.xmlHttpReq.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
		self.xmlHttpReq.onreadystatechange = function() {
			if (self.xmlHttpReq.readyState == 4) {
				update_page(self.xmlHttpReq.responseXML, strURL);
			}
		}
		self.xmlHttpReq.send(get_page_args());

	} catch (exception) {
		alert(exception);
	}


}


function get_page_args () {

	var args = "ajax=1";

	var cnodes = document.getElementsByTagName('input');
	for (var i = 0; i < cnodes.length; i++) {
		var cname = cnodes[i].getAttribute('name');

		if (cname) {
			args = args + "&amp;" + cname + "=" + cnodes[i].value;
		} 
		
	}

	cnodes = document.getElementsByTagName('select');
	for (var i = 0; i < cnodes.length; i++) {
		var cname = cnodes[i].getAttribute('name');

		if (cname) {
			args = args + "&amp;" + cname + "=" + cnodes[i].value;
		} 
		
	}

	
	return args;

}



function update_page(xml, strURL) {


	//var updates = xml.getElementsByName("ajaxUpdates");
	var updates = xml.getElementsByTagName("update");

	for (var i = 0; i < updates.length; i++) {
		var id = updates[i].getAttribute("id");
		var attr = updates[i].getAttribute("attr");

		if (document.getElementById(id)) {
			if (attr == "innerHTML") {
				var obj = document.getElementById(id);
				obj.innerHTML = updates[i].firstChild.nodeValue;
			} else if (attr == "value") {
				var obj = document.getElementById(id);
				obj.value = updates[i].firstChild.nodeValue;
			} else if (attr == "className") {
				var obj = document.getElementById(id);
				obj.className = updates[i].firstChild.nodeValue;
			}
		}

	}
	date_refresh();
	schedule_update(strURL);
}


function schedule_update(strURL) {

	// figure out if we should schedule another page update
	var reload = document.getElementById("ajaxEnabled").value;

	if (reload == "yes" && document.getElementById("ajaxTimeout")) {
		var timeout = document.getElementById("ajaxTimeout").value;
		if (timeout < 1) { timeout = 5; }
		// if still enabled, schedule another update
		self.setTimeout("xmlHttpPost(\'" + strURL + "\')", timeout * 1000);
	}

}


function update_status(message) {
	document.getElementById("ajaxStatusMessage").innerHTML = message;
	date_refresh();
}

function date_refresh() {
	document.getElementById("ajaxUpdated").innerHTML = get_date();
}


function get_date() {

	var d = new Date();
	var dateStr = d.toUTCString();
	return dateStr;

}


function synchTab(frameName) {
	var elList, i;

	// Exit if no frame name was given
	if (frameName == null) {
		return;
	}

	// Check all links
	elList = document.getElementsByTagName("A");
	for (i = 0; i < elList.length; i++) {

		// Check if the link's target matches the frame being loaded
		if (elList[i].target == frameName) {

			// If the link's URL matches the page being loaded, activate it
			// Otherwise, make sure the tab is deactivated
			if (elList[i].href == window.frames[frameName].location.href) {
				elList[i].className += " activeTab";
				elList[i].blur();
			} else {
				removeName(elList[i], "activeTab");
			}
		}
	}

}


function removeName(el, name) {

	var i, curList, newList;

	// Remove the given class name from the element's className property
	newList = new Array();
	curList = el.className.split(" ");
	for (i = 0; i < curList.length; i++) {
		if (curList[i] != name) {
			newList.push(curList[i]);
		}
	}
	el.className = newList.join(" ");
}


function update_element_value(elementName, elementValue) {

	if (document.getElementById(elementName)) {
		var obj = document.getElementById(elementName);
		obj.value = elementValue;
		alert("Updated: " + elementName + " to " + elementValue);
	} else {
		//alert("Not Updating: " + elementName);
	}
		

}

function input_value_changed (inputObj) {

	var styleObj = inputObj.style;
	if (styleObj) {
		styleObj.backgroundColor = "#990000";
		styleObj.color = "#cccccc";
	}
}
