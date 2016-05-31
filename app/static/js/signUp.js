/**
 * Created by b5053043 on 29/05/2016.
 */
$(function(){
	//$('#btnSignUp').click(function(){
    //
	//	$.ajax({
	//		url: '/signUp',
	//		data: $('form').serialize(),
	//		type: 'POST',
	//		success: function(response){
	//			console.log(response);
	//		},
	//		error: function(error){
	//			console.log(error);
	//		}
	//	});
	//});
});

// Signing into the application
$(function(){
	//$('#btnSignIn').click(function(){
    //
	//	$.ajax({
	//		url: '/signIn',
	//		data: $('form').serialize(),
	//		type: 'POST',
	//		success: function(response){
	//			console.log(response);
	//		},
	//		error: function(error){
	//			console.log(error);
	//		}
	//	});
	//});
});

$(function(){
    var options = {
       type: 'video',
       frameInterval: 20 // minimum time between pushing frames to Whammy (in milliseconds)
    };
    var recordRTC = RecordRTC(mediaStream, options);
    recordRTC.startRecording();
    recordRTC.stopRecording(function(videoURL) {
        video.src = videoURL;
        var recordedBlob = recordRTC.getBlob();
        var recordedUrl = recordRTC.getDataURL(function(dataURL) { });
    });
});