function singleThumb(){
	console.log("singleThumb INVOKED");
	timeSlider1 = dijit.byId("esri_dijit_TimeSlider_0");
	timeSlider1.setThumbCount(1);
	timeSlider1.singleThumbAsTimeInstant(true);
}

function dojoSingleThumb(){
	console.log("dojoSingleThumb INVOKED");
	require(["dojo/ready"],
	function(ready){
		ready(singleThumb);
	});
}

function onFrameLoad(){
	console.log("IFRAME LOADED");
	iframe = this;
	iframewindow = iframe.contentWindow || iframe.window || (iframe.contentDocument ? iframe.contentDocument.defaultView: iframe);
	iframewindow.eval(dojoSingleThumb.toString());
}
