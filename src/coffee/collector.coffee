((window, $) ->
  mainPanel = $ "##{window.o.pageVars.mainPanelId}"
  propagatingItemSelectors = [
    'a.file-list-link',
    'a.file-list-download'
  ]
  # a click event handler must be directly attached to these elements as
  # their other handlers are preventing event propagation, so the outer
  # mainPanel selector is never reached.
  nonPropagatingItemSelectors = [
    '.playlist-list-item-link',
    '.gallery-list-item-link'
  ]
  typeMapping = {
    file: "file",
    directory: "folder",
    download: "download"
  }

  collectEvent = (path, type) ->
    ($ window).trigger 'analytics-collect', [{path: path, type: type}]

  listItemClicked = (e) ->
    el = $(@)
    # in some cases, the metadata is stored on the wrapping <li> element,
    # while in other cases on the link element itself. to avoid breaking
    # existing code that depends on that structure, we allow both cases
    # and pick the parent element automatically if the data is not found
    # on the link element itself.
    if not el.data('type')?
      el = el.parent()

    path = el.data('relpath')
    itemType = typeMapping[el.data('type')]
    mimeType = el.data('mimetype') or ''
    # ignore portion of mimetype after the slash
    mimeType = mimeType.substring(0, mimeType.indexOf("/"))
    if window.collectEvent?
      data = {path: path, type: (mimeType or itemType)}
      window.collectEvent data

  mainPanel.on 'click', propagatingItemSelectors.join(), listItemClicked
  for idx, selector of nonPropagatingItemSelectors
    $(selector).on 'click', listItemClicked

  return

) this, this.jQuery

