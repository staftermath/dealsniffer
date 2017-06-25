function ChangeSelected(target) {
	$(target).on("change",function(){
	  $("option[value=" + target.value + "]", target)
	  .attr("selected", true).siblings()
	  .removeAttr("selected")
	});
}

function GetDeal(deal, targetid, url) {
	var url = url + "?deal="+ deal;
	// var template = '<iframe type="text/html" data="%URL%" style="height:100%; width:100%;"></object>';
	// var newinnerHTML = template.replace("%URL%", url);
 //    document.getElementById(targetid).innerHTML = newinnerHTML
 	$("#"+targetid).load(url)
	

}