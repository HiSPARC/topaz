Questions

- Does the trigger pattern only take signals in the coincidence window
  into account or also the pre/post?

- Why can/should the post-coincidence window not be shorter than the
  coincidence window?

- Could a 'second' pulse causing the trigger (i.e. 2-high) in a
  coincidence also be the start of the coincidece time for a
  following trigger? (if len(cointime) > len(posttime))

- A coincidence can not happen in a post coincidence window.

- Does the coincidence time for 4 detector stations in a 2-high
  triggered event start when the first detector has 1 low or 1 high?

- Is the trigger blind to other pulses in the same channel during the
  'coincidence time' after a pulse
