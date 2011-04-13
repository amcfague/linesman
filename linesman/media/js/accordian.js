$(function(){
    var slideSpeed = "fast";
    $('#callhierarchy .row').click(function() {
        // navigate up to the nearest parent list item
        var parent_li = $(this).parent('li');
        parent_li.children('ul').toggle(slideSpeed);
        parent_li.toggleClass('open closed');
    });
});
