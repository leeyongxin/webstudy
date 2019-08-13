function showCustomer(value) {
  alert(value);
  alert("success");
}

function showpic(event) {
  $.ajax({
    url: event.data.para1,
    
    type: 'get', // This is the default though, you don't actually need to always mention it
    dataType: 'json',
    success: function (data) {
      var picstring = "data:image/png;base64," + data['p1']
      $("#pic").attr("src", picstring)
    },
    failure: function (data) {
      alert('Got an error dude');
    }
  });
}