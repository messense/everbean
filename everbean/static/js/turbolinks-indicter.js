jQuery(document).ready(function ($) {
   $(document).on('page:load', function () {
       $('#loading').hide();
       if ($('textarea#content').length > 0) {
           if ($('.CodeMirror').length == 0) {
               var editor = new Editor({
                   element: document.getElementById('content'),
                   status: false
               });
               editor.render();
           }
       }
   });
   $(document).on('page:fetch', function () {
       $('#loading').show();
   });
});