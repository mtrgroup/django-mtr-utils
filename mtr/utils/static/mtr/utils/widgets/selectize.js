$(document).ready(function() {
    $('[data-selectize-select]').each(function() {
        var item = $(this);
        var itemSelectize;

        item.selectize({
            valueField: 'id',
            labelField: 'full_name',
            searchField: 'name',
            width: '220px',
            persist: false,
            load: function(query, callback) {
                itemSelectize.clearOptions();

                if (!query.length) return callback();

                var params = item.data('params') || {};
                params['query'] = query;

                $.ajax({
                    url: item.data('selectize-select'),
                    data: params,
                    type: 'GET',
                    error: function() {
                        callback();
                    },
                    success: function(res) {
                        itemSelectize.clearOptions();
                        callback(res.items);
                    }
                });
            }
        });

        itemSelectize = item[0].selectize;
    });
});
