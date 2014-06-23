search = ->
  books = new Bloodhound
    datumTokenizer: (d) ->
      Bloodhound.tokenizers.whitespace d.title
    queryTokenizer: Bloodhound.tokenizers.whitespace
    remote: "/api/book/search?q=%QUERY"

  books.initialize()

  $('#search .typeahead').typeahead null,
    name: 'books'
    displayKey: 'title'
    source: books.ttAdapter()

$(document).on "page:load", search

$(document).ready search
