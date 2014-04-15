jQuery(document).ready(function ($) {
  $(document).on('click', '.eb-box-close', function () {
      var dismiss = $(this).attr('data-dismiss');
      var show = $(this).attr('data-show');
      $(dismiss).hide();
      if (show.length > 0) {
        $(show).fadeIn('slow');
      }
      return false;
  });
  $(document).on('click', '.js-book', function () {
      var book = $(this).parent().parent();
      var target = $(this).attr('data-target');
      $('.js-create-note .eb-book-info ul').html(book.clone(true));
      $('#create-note').attr('action', '/note/create/' + target)
      $('#book_id').attr('value', target);
      $('.js-create-note').slideDown();
      $('.eb-books-reading').hide();
      return false;
  });
});