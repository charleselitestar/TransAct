document.addEventListener("DOMContentLoaded", function () {
  // Assuming you have connected to the Socket.IO server
  var socket = io.connect("http://" + document.domain + ":" + location.port);

  function get_update(){
    var acc_balance = document.getElementById("accountBalance").value;
    console.log(acc_balance)
    socket.emit('update_balance', {amount: acc_balance});
  }
  // Listen for the 'update_balance' event
  socket.on("update_balance", function (data) {
    console.log('new balance', data.amount);
    // Update the UI with the new balance data
    var new_balance = data.amount
    document.getElementById("accountBalance").innerHTML = new_balance;
  });

  get_update()
});
