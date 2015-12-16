((window, $) ->
  TRACK_PATH = 'analytics'


  getTrackingUrl = () ->
    locale = (window.location.pathname.split '/')[1]
    "/#{locale}/#{TRACK_PATH}/"


  processEvent = (e, data) ->
    data.path = decodeURIComponent(data.path)
    res = $.ajax
      url: getTrackingUrl()
      type: 'POST'
      data: data
      async: false
    res.done (data) ->
      console.log data


  ($ window).on 'opener-click', processEvent

) this, this.jQuery
