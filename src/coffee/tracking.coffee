((window, $) ->
  TRACK_PATH = 'analytics'


  getTrackingUrl = () ->
    locale = (window.location.pathname.split '/')[1]
    "/#{locale}/#{TRACK_PATH}/"


  processEvent = (e, data) ->
    data.path = decodeURIComponent(data.path)

    # We are deliberately doing a *synchronous* AJAX call here. This allows us
    # to circumvent the problem with asynchronous AJAX calls not completing
    # when browser is moving away from the page on which the AJAX call was
    # started. As a side-effect, the page blocks while the request is being
    # processed. We don't yet know if this poses a significant problem during
    # normal usage.
    res = $.ajax
      url: getTrackingUrl()
      type: 'POST'
      data: data
      async: not (data.type in ['folder', 'download'])
    return


  ($ window).on 'opener-click', processEvent

) this, this.jQuery
