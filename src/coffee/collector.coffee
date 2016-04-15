((window, $) ->
  selectors = {
    fileOpenListItem: 'a.file-list-link',
    fileDownloadListItem: 'a.file-list-control',
    videoPlayListItem: '.views-sidebar-video .playlist-list-item-link',
    audioPlayListItem: '.views-sidebar-audio .playlist-list-item-link',
    galleryListItem: '.gallery-list-item-link'
  }

  collectEvent = (path, type) ->
    ($ window).trigger 'analytics-collect', [{path: path, type: type}]

  fileOpenListItemClicked = (e) ->
    el = $(@)
    if el.data('mimetype') == 'html' 
      collectEvent el.attr('href'), 'html'
    else if el.data('type') == 'directory'
      collectEvent el.attr('href'), 'folder'
    else 
      collectEvent el.attr('href'), 'file'

  fileDownloadListItemClicked = (e) ->
    el = $(@)
    collectEvent el.attr('href'), 'download'

  audioPlayListItemClicked = (e) ->
    el = $(@).parent()
    collectEvent el.data('direct-url'), 'audio'

  videoPlayListItemClicked = (e) ->
    el = $(@).parent()
    collectEvent el.data('direct-url'), 'video'

  galleryListItemClicked = (e) ->
    el = $(@).parent()
    collectEvent el.data('direct-url'), 'image'

  $(selectors.fileOpenListItem).click fileOpenListItemClicked
  $(selectors.fileDownloadListItem).click fileDownloadListItemClicked
  $(selectors.audioPlayListItem).click audioPlayListItemClicked
  $(selectors.videoPlayListItem).click videoPlayListItemClicked
  $(selectors.galleryListItem).click galleryListItemClicked

  return

) this, this.jQuery

