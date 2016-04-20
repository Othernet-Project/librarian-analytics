((window, $) ->
  TRACK_PATH = 'analytics'
  LOCALE = (window.location.pathname.split '/')[1]
  TZ_OFFSET = - (new Date()).getTimezoneOffset() / 60.0

  getTrackingUrl = () ->
    "/#{LOCALE}/#{TRACK_PATH}/"

  decode = (data) ->
    while (decodeURIComponent(data) != data)
      data = decodeURIComponent(data)
    return data

  window.collectEvent = (data) ->
    data.path = decode(data.path)
    data.tz = TZ_OFFSET
    # We are deliberately doing a *synchronous* AJAX call here. This allows us
    # to circumvent the problem with asynchronous AJAX calls not completing
    # when browser is moving away from the page on which the AJAX call was
    # started. As a side-effect, the page blocks while the request is being
    # processed. We don't yet know if this poses a significant problem during
    # normal usage.
    $.ajax
      url: getTrackingUrl()
      type: 'POST'
      data: data
      async: data.type in ['folder'],

    return

  return

) this, this.jQuery
