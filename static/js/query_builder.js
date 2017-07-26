var myFilters = [
{
    id: 'price',
    label: 'Price',
    type: 'string'
}, {
    id: 'name',
    label: 'Name',
    type: 'string',
}, {
    id: 'description',
    label: 'Description',
    type: 'string'
}];

$('#builder-output-columns').queryBuilder({
    plugins: ['bt-tooltip-errors'],
    allow_groups: false,
    conditions: ['AND'],
    operators: [{ type: 'display_as', optgroup: 'custom', nb_inputs: 1, multiple: false, apply_to: ['string']}],
    lang: {
            operators: {
                display_as: 'display as',
            }
        },

    filters: myFilters,

    rules: {
              condition: 'AND',
              rules: [
                  {
                    id: 'name',
                    operator: 'display_as',
                    value: ''
                  }
                ]
            }
});

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

$('.group-conditions').hide();

var bt = $('#builder-output-columns button[data-add = "rule"]');
bt.html(bt.html().replace('Add rule', 'Add column'));


// --------------------------------------------------------------------------------------------------

var myFilters = [
{
    id: 'price',
    label: 'Price',
    type: 'double'
}, {
    id: 'name',
    label: 'Name',
    type: 'string',
    operators: ['contains','contains_one','contains_near', 'regex']
}, {
    id: 'description',
    label: 'Description',

    type: 'string'
}];

$('#builder-data-filter').queryBuilder({
    plugins: ['bt-tooltip-errors'],

        operators: $.fn.queryBuilder.constructor.DEFAULTS.operators.concat([
            { type: 'contains_one',  nb_inputs: 1, multiple: false, apply_to: ['string'] },
            { type: 'contains_near',	nb_inputs: 2, multiple: false, apply_to: ['string'] },
            { type: 'regex',	nb_inputs: 1, multiple: false, apply_to: ['string'] }
        ]),

    lang: {
            operators: {
                contains_one: 'contains any',
                contains_near: 'contains by distance',
                regex: 'regular expressions'
            }
        },

    filters: myFilters,

    rules: {
              condition: 'AND',
              rules: [
                  {
                    id: 'name',
                    operator: 'contains_near',
                    value: ['Hello World','5']
                  }
                ]
            }
});

$('.reset-data-filter').on('click', function() {
    $('#builder-data-filter').queryBuilder('reset');
});
