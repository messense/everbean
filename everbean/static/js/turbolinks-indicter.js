jQuery(document).ready(function ($) {
   $(document).on('page:load', function () {
       $('#loading').hide();
   });
   $(document).on('page:fetch', function () {
       $('#loading').show();
   });
});