$(document).on 'page:load', ->
  $('#loading').hide()
  if $('#content').length > 0 and $('.CodeMirror').length is 0
    editor = new Editor
      element: document.getElementById('content'),
      status: false
    editor.render()

$(document).on 'page:fetch', ->
  $('#loading').show();