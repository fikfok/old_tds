$(function() {
    $('#files-list').on('change', function () {
        $('#files-list-table-body').append('<tr><td>' + $("#files-list")[0].files[0].name + '</td><td>' + $("#files-list")[0].files[0].size + '</td><td><progress id="upload-progress-bar" max="100" value="0" style="width: 70px;"></progress></td><td><progress id="indexing-progress-bar" max="100" value="0" style="width: 70px;"></progress></td></tr>');
        $('#submit-upload-files').click();
    });

    $('#upload-files-form').on('submit', function(event){
        event.preventDefault();

        var data = new FormData();
        data.append('file_name', $("#files-list")[0].files[0].name);
        data.append('file_size', $("#files-list")[0].files[0].size);
        data.append('file', $("#files-list")[0].files[0]);
        data.append('submit-upload-files', 'upload files');
        data.append('csrfmiddlewaretoken', $('input[name="csrfmiddlewaretoken"]').val());
        $.ajax({

            xhr: function() {
            var xhr = new window.XMLHttpRequest();

            xhr.upload.addEventListener("progress", function(evt) {
                if (evt.lengthComputable) {
                    var percentComplete = parseInt((evt.loaded / evt.total) * 100);
                    $('#upload-progress-bar').attr('value', percentComplete);
                    if (percentComplete === 100) {
                        $('#upload-progress-bar').attr('value', '100');
                        console.log('Done!');
                    }
                  }
                }, false);
            return xhr;
            },

            url : "",
            type : "POST",
            data : data,
            processData: false,
            contentType: false,
            success : function(json){
                console.log("success");
                var index_name = json['index_name'];
                var intervalID = setInterval(function testFunc(){
                       $.ajax({
                            url : "task_status/" + json['task_id'],
                            type : "POST",
                            data : data,
                            processData: false,
                            contentType: false,
                            success : function(json){
                                    if (parseInt(json['indexing_status']) >= 0 && $('#indexing-progress-bar').attr('value') < parseInt(json['indexing_status'])) {
                                        $('#indexing-progress-bar').attr('value', parseInt(json['indexing_status']));
                                    };
                                    if (parseInt(json['indexing_status']) >= 100) {
                                        clearInterval(intervalID);
                                        $.ajax({
                                             url : "get_data_from_" + index_name + "_between_0_and_200",
                                             type : "POST",
                                             data : data,
                                             processData: false,
                                             contentType: false,
                                             success : function(json){
                                                    var columns_list = []
                                                    $.each(json['response_es_data'], function(row_num, row_in_json_table){
                                                        if(row_num == 0){
                                                            for(i = 0; i < row_in_json_table.length; i++){
                                                                columns_list.push({id: 'col_num_' + i.toString(), label: 'Col #' + (i + 1).toString(), type: 'string'});
                                                            };
                                                        };

                                                        var row = $("<tr />");
                                                        $("#table-content").append(row);
                                                        $.each(row_in_json_table, function(col_num, cell_in_json_table){
                                                            row.append($("<td>" + cell_in_json_table + "</td>"));
                                                        });
                                                    });

                                                    $('#builder-output-columns').queryBuilder({
                                                        plugins: ['bt-tooltip-errors'],
                                                        allow_groups: false,
                                                        conditions: ['AND'],
                                                        operators: [{ type: 'display_as', optgroup: 'custom', nb_inputs: 1, multiple: false, apply_to: ['string']}],
                                                        lang: {operators: {display_as: 'display as'}},
                                                        filters: columns_list
                                                    });

                                                    $('.column-builder-container .group-conditions').hide();

                                                    var bt = $('#builder-output-columns button[data-add = "rule"]');
                                                    bt.html(bt.html().replace('Add rule', 'Add column'));

                                                 },
                                             error : function() {
                                                 console.log("error")
                                             }
                                         })
                                    }
                                },
                            error : function() {
                                console.log("error")
                            }
                        });
                    },
                    300);
            },
            error : function(xhr,errmsg,err) {
                console.log("error")
            }
        });

        $("#files-list").val('');
    });
});

$('.nav-tabs li').on('click', function() {
    if ($(this).html().indexOf('Filters') > 0 && !($(this).hasClass('active'))) {
        alert('First push');
    }
});
