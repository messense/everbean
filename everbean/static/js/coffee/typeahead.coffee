search = ->
  $('#search').on "submit", ->
    false

  books = new Bloodhound
    datumTokenizer: (d) ->
      Bloodhound.tokenizers.whitespace d.title
    queryTokenizer: Bloodhound.tokenizers.whitespace
    remote:
      url: "/api/book/search?q=%QUERY"
      ajax:
        beforeSend: ->
          NProgress.start()
        complete: ->
          NProgress.done()

  books.initialize()

  $('#search .typeahead').typeahead null,
    name: "books"
    displayKey: "title"
    source: books.ttAdapter()
    templates:
      empty: "<p>Oops, 找不到任何相关的书籍！</p>"
      suggestion: (context, options) ->
        """
        <div class="book-search-item clearfix" id="book-#{context['douban_id']}" data-book-id="#{context['douban_id']}">
          <div class="book-search-item-cover"><img src="#{context['image']}" alt="" width="30" height="40" /></div>
          <div class="book-search-item-info">
            <p><strong>#{context['title']}</strong></p>
            <p><small>#{context['author']}</small></p>
          </div>
        </div>
        """

$(document).on "page:load", search

$(document).ready search

$(document).on "typeahead:selected", (event, book) ->
  url = "/book/search/#{book.douban_id}"
  window.open(url)
