$(function(){
  // get from the server the current number of tweets
  function update_count(){
    $.ajax('/count').done(function(data){
      $('#tweets').text(data.count)
    })
  }
  // get on initialization
  update_count()
  // get every five seconds
  setInterval(update_count, 5000)
})