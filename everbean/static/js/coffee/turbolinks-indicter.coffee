NProgress.configure
  showSpinner: false

$(document).on "page:load", ->
  NProgress.done()
  if $("#content").length > 0 and $(".CodeMirror").length is 0
    editor = new Editor
      element: document.getElementById("content"),
      status: false
    editor.render()

$(document).on "page:fetch", ->
  NProgress.start()

$(document).on "page:restore", ->
  NProgress.remove()
