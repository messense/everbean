$(document).on 'page:load', ->
  $('#loading').hide()
  if $('textarea#content').length > 0
    if $('.CodeMirror').length is 0
      editor = new Editor({
        element: document.getElementById('content'),
        status: false
      })
      editor.render()

$(document).on 'page:fetch', ->
  $('#loading').show();