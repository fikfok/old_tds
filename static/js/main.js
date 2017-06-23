$(function() {
    $('#files-list').on('change', function () {
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
            url : "",
            type : "POST",
            data : data,
            processData: false,
            contentType: false,
            success : function(json) {
                console.log("success");
                $('#files-list-table-body').append('<tr><td>' + json['response_file_name'] + '</td><td>' + json['response_file_type'] + '</td><td>' + json['response_file_size'] + '</td></tr>');
                $("#files-list").val('');
                $.each(json['response_es_data']['data'], function(key_in_json_table, row_in_json_table){
                    var row = $("<tr />");
                    $("#table-content").append(row);
                    $.each(row_in_json_table, function(key_in_json_row, cell_in_json_table){
                        console.log(cell_in_json_table);
                        row.append($("<td>" + cell_in_json_table + "</td>"));
                    });
                })
            },
            error : function(xhr,errmsg,err) {
                console.log("error")
            }
        });
    });
});