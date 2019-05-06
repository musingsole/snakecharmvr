var yes_last_event = null
var yes_cumulative_ydelta = 0
var yes_cumulative_decline = 0
var yes_started = false
var yes_complete = false
var yes_start_time = new Date()
var yes_timeout = 200
var yes_window = 100

function yeslistener(event){
  if (yes_last_event !== null && yes_complete == false){
    var ydelta = event.y - yes_last_event.y
    if (ydelta < 0) {
      if (yes_started == false){
        yes_started = true
        yes_cumulative_decline = 0
        yes_cumulative_decline = 0
      }
      yes_cumulative_ydelta = yes_cumulative_ydelta + ydelta
    } else if (ydelta > 0) {
      if (yes_cumulative_decline > yes_window && yes_started == true && yes_complete == false){
        var delta_time = ((new Date()).getTime() - yes_start_time.getTime()) / 1000
        if (delta_time > 0.1 && yes_cumulative_ydelta < -yes_window) {
          yes_complete = true
          yes_started = false
          console.log("Yes completed")
          setTimeout(function(){
            yes_complete = false
            console.log("Resetting yes_complete")}, yes_timeout)
        } else {
          yes_complete = false
          yes_started = false
          console.log("Yes aborted")
        }
      }
      yes_cumulative_decline = yes_cumulative_decline + ydelta
    }
  }
  yes_last_event = event
}
