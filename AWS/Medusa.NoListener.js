var no_last_event = null
var no_cumulative_ydelta = 0
var no_cumulative_decline = 0
var no_started = false
var no_complete = false
var no_start_time = new Date()
var no_timeout = 200
var no_window = 100

function nolistenter(event){
  if (no_last_event !== null && no_complete == false){
    var ydelta = event.y - no_last_event.y
    if (ydelta < 0) {
      if (no_started == false){
        no_started = true
        no_cumulative_decline = 0
        no_cumulative_decline = 0
      }
      no_cumulative_ydelta = no_cumulative_ydelta + ydelta
    } else if (ydelta > 0) {
      if (no_cumulative_decline > no_window && no_started == true && no_complete == false){
        var delta_time = ((new Date()).getTime() - no_start_time.getTime()) / 1000
        if (delta_time > 0.1 && no_cumulative_ydelta < -no_window) {
          no_complete = true
          no_started = false
          console.log("Yes completed")
          setTimeout(function(){
            no_complete = false
            console.log("Resetting no_complete")}, no_timeout)
        } else {
          no_complete = false
          no_started = false
          console.log("Yes aborted")
        }
      }
      no_cumulative_decline = no_cumulative_decline + ydelta
    }
  }
  no_last_event = event
}
