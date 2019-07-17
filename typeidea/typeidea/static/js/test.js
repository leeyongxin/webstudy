function showCustomer(value) {
  alert(value);
  alert("success");
}

function test2(event) {
  var urlstr = '/js_d'+event.data.para1+'/'
  $.ajax({
    url: event.data.para2,
    
    type: 'get', // This is the default though, you don't actually need to always mention it
    dataType: 'json',
    success: function (data) {
      var picstring = "data:image/png;base64," + data['p1']
      alert(picstring)
      $("#pic").attr("src", picstring)
    },
    failure: function (data) {
      alert('Got an error dude');
    }
  });
}