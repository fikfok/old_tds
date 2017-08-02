$('#btn-reset').on('click', function() {
    $('#builder-output-columns').queryBuilder('reset');
});

$('#btn-set').on('click', function() {
    $('#builder-output-columns').queryBuilder('setRules', rules_basic);
});

$('#btn-get').on('click', function() {
    var result = $('#builder-output-columns').queryBuilder('getRules');

    if (!$.isEmptyObject(result)) {
        alert(JSON.stringify(result, null, 2));
    }
});

// reset builder
$('.reset-column-builder').on('click', function() {
    $('#builder-output-columns').queryBuilder('reset')
});

// set rules
$('.set-json').on('click', function() {
    var target = $(this).data('target');
    var rules = window['rules_' + target];

    $('#builder-' + target).queryBuilder('setRules', rules);
});

// get rules
$('.parse-json').on('click', function() {
    var target = $(this).data('target');
    var result = $('#builder-' + target).queryBuilder('getRules');

    if (!$.isEmptyObject(result)) {
        bootbox.alert({
            title: $(this).text(),
            message: '<pre class="code-popup">' + format4popup(result) + '</pre>'
        });
    }
});

function format4popup(object) {
    return JSON.stringify(object, null, 2).replace(/</g, '&lt;').replace(/>/g, '&gt;')
}


// --------------------------------------------------------------------------------------------------

$('.reset-data-filter').on('click', function() {
    $('#builder-data-filter').queryBuilder('reset');
});
