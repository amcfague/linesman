$(function(){
    var slideSpeed = "normal";
    $('#callhierarchy .row').click(function() {
        // callhierarchyigate up to the nearest parent list item
        var parent_li = $(this).closest('li');
        if ($(parent_li).children('ul').html() != null) {
            $(parent_li).parent('ul').children('li').children('ul').hide(slideSpeed);
            $(this).delay(100).is(':hidden');
            if ($(parent_li).children('ul').css('display') == "block") {
                $(parent_li).children('ul').hide(slideSpeed);
                $(parent_li).removeClass('open');
                $(parent_li).addClass('closed');
            } else {
                $(parent_li).children('ul').show(slideSpeed);
                $(parent_li).removeClass('closed');
                $(parent_li).addClass('open');
            }
            return false;
        }
        // Handle leaf nodes here; just return a constant false, so that the
        // page position doesn't change when clicking the node.
        else if($(parent_li).hasClass('leaf')) {
            return false;
        }
    });

    $('#callhierarchy li').each(function() {
        // Is this a leaf?  If so, set the "leaf" class.
        if($(this).find('ul').length == 0) {
            $(this).removeClass('open closed');
            $(this).addClass('leaf');
        }
        else if ($(this).children('ul').length > 0) {
            if ($(this).children('ul').is(":visible")) {
                $(this).removeClass('closed');
                $(this).addClass('open');
            }
            else {
                $(this).removeClass('open');
                $(this).addClass('closed');
            }
        }
    });
});
