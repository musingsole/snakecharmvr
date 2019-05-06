// Written by yeslistender, read by whoever
var yes_last_event = null
var yes_cumulative_rise = 0
var yes_cumulative_decline = 0
var yes_started = false
var yes_complete = false
var yes_start_time = new Date()
var yes_timeout = 200
var yes_window = 100


// Written by nolistener, read by whoever
var no_last_event = null
var no_cumulative_rise = 0
var no_cumulative_decline = 0
var no_started = false
var no_complete = false
var no_start_time = new Date()
var no_timeout = 200
var no_window = 100


function yeslistener(event){
  if (yes_last_event !== null && yes_complete == false){
    var ydelta = event.y - yes_last_event.y
    if (ydelta < 0) {
      if (yes_started == false){
        yes_started = true
        yes_cumulative_rise = 0 //Will be negative when moving up
        yes_cumulative_decline = 0 //Will be positive when moving down
      }
      yes_cumulative_rise = yes_cumulative_rise + ydelta
    } else if (ydelta > 0) {
      if (yes_started == true && yes_complete == false){
        var delta_time = ((new Date()).getTime() - yes_start_time.getTime()) / 1000
        if (delta_time > 0.15 && yes_cumulative_rise < -yes_window) {
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
          console.log(yes_cumulative_rise)
          console.log(yes_cumulative_decline)
        }
      }
      yes_cumulative_decline = yes_cumulative_decline + ydelta
    }
  }
  yes_last_event = event
}


function nolistener(event){
  if (no_last_event !== null && no_complete == false){
    var ydelta = event.y - no_last_event.y
    if (ydelta > 0) {
      if (no_started == false){
        console.log("no started")
        no_started = true
        no_cumulative_decline = 0
        no_cumulative_rise = 0
      }
      no_cumulative_rise = no_cumulative_rise + ydelta
    } else if (ydelta < 0) {
      if (no_cumulative_decline < no_window && no_started == true && no_complete == false){
        var delta_time = ((new Date()).getTime() - no_start_time.getTime()) / 1000
        if (delta_time > 0.1 && no_cumulative_rise > no_window) {
          no_complete = true
          no_started = false
          console.log("No completed")
          setTimeout(function(){
            no_complete = false
            console.log("Resetting no_complete")}, no_timeout)
        } else {
          no_complete = false
          no_started = false
          console.log("No aborted")
        }
      }
      no_cumulative_decline = no_cumulative_decline + ydelta
    }
  }
  no_last_event = event
}


function devicelistener(event){
    // Get selected device from aframe?
    // IF Modifiable Device Selected
    // IF YES_COMPLETED
    if (yes_complete == true){
        // CAPTURE X-axis movement like yeslistener
        // Scaled to input, build translucent a-frame projection
    }
}