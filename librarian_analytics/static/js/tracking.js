// Generated by CoffeeScript 1.10.0
(function(window, $) {
  var TRACK_PATH, getTrackingUrl, processEvent;
  TRACK_PATH = 'analytics';
  getTrackingUrl = function() {
    var locale;
    locale = (window.location.pathname.split('/'))[1];
    return "/" + locale + "/" + TRACK_PATH + "/";
  };
  processEvent = function(e, data) {
    var ref, res;
    data.path = decodeURIComponent(data.path);
    res = $.ajax({
      url: getTrackingUrl(),
      type: 'POST',
      data: data,
      async: !((ref = data.type) === 'folder' || ref === 'download')
    });
  };
  return ($(window)).on('opener-click', processEvent);
})(this, this.jQuery);
