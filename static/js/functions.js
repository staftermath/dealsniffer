function ChangeSelected(target) {
	$(target).on("change",function(){
	  $("option[value=" + target.value + "]", target)
	  .attr("selected", true).siblings()
	  .removeAttr("selected")
	});
}

function GetDeal(deal, targetid, url) {
    var url = url + "?deal="+deal; //+ "&parser=" + parser;
    var template = '<object type="text/html" data="%URL%" style="height:100%; width:100%;"></object>';
    document.getElementById(targetid).innerHTML = template.replace("%URL%", url)
}