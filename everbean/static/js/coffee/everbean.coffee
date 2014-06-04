$(document).on 'click', '.eb-box-close', ->
  dismiss = $(this).attr 'data-dismiss'
  show = $(this).attr 'data-show'
  $(dismiss).hide()
  if show.length > 0
    $(show).fadeIn 'slow'
  false

$(document).on 'click', '.js-book', ->
  book = $(this).parent().parent()
  target = $(this).attr 'data-target'
  $('.js-create-note .eb-book-info ul').html book.clone(true)
  $('.eb-book-info .js-book').removeClass 'js-book'
  $('#create-note').attr 'action', '/note/create/#{target}'
  $('#book_id').attr 'value', target

  if $('#content').length > 0 and $('.CodeMirror').length is 0
    editor = new Editor({
      element: document.getElementById('content'),
      status: false
    })
    editor.render()

  $('.js-create-note').show()
  $('.eb-books-reading').hide()
  false
