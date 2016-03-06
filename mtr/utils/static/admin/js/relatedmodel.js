$(document).ready(function() {

$('[data-model-info]').each(function() {
    var item = $(this);
    item.load(item.data('model-info'));
});

$('[data-model-choose], [data-model-edit]').on('click', function(e) {
    var item = $(this);
    e.preventDefault();

    var windowWidth = $(window).width();
    var windowHeight = $(window).height();

    windowWidth = parseInt(windowWidth - windowWidth / 8);
    windowHeight = parseInt(windowHeight - windowHeight / 8);

    var name = 'id_' + item.parent().find('input[type="hidden"]').attr('name');

    var child = window.open(
        item.attr('href'), name,
        'height='+windowHeight+',width='+windowWidth+',resizable=yes,scrollbars=yes');

    var timer = setInterval(checkChild, 500);

    function checkChild() {
        if (child.closed) {
            var info = item.parent().find('[data-model-info]');

            parts = info.data('model-info').split('/');
            parts[parts.length-1] = $('#' + name).val();

            info.load(parts.join('/'));

            clearInterval(timer);
        }
    }
});

});
