((window, $) ->
  TRACK_PATH = 'analytics'
  LOCALE = (window.location.pathname.split '/')[1]
  TZ_OFFSET = - (new Date()).getTimezoneOffset() / 60.0
  URL_ROOT = "/direct"
  FOLDER_ROOT = "/#{LOCALE}/files"

  getTrackingUrl = () ->
    "/#{LOCALE}/#{TRACK_PATH}/"

  decode = (data) ->
    while (decodeURIComponent(data) != data)
      data = decodeURIComponent(data)
    return data

  stripRoot = (data) ->
    data.replace(URL_ROOT, "").replace(FOLDER_ROOT, "")

  recordEvent = (e, data) ->
    data.path = stripRoot(decode(data.path))
    data.tz = TZ_OFFSET
    # We are deliberately doing a *synchronous* AJAX call here. This allows us
    # to circumvent the problem with asynchronous AJAX calls not completing
    # when browser is moving away from the page on which the AJAX call was
    # started. As a side-effect, the page blocks while the request is being
    # processed. We don't yet know if this poses a significant problem during
    # normal usage.
    console.log data
    res = $.ajax
      url: getTrackingUrl()
      type: 'POST'
      data: data
      async: not (data.type in ['file', 'download'])
    return

  ($ window).on 'analytics-collect', recordEvent

  return

) this, this.jQuery
