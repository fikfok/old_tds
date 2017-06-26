$(function() {
    $('#files-list').on('change', function () {
        $('#files-list-table-body').append('<tr><td>' + $("#files-list")[0].files[0].name + '</td><td>' + $("#files-list")[0].files[0].size + '</td><td><progress id="upload-progress-bar" max="100" value="0" style="width: 70px;"></progress></td></tr>');
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
            success : function(json) {
                console.log("success");
                $.each(json['response_es_data']['data'], function(key_in_json_table, row_in_json_table){
                    var row = $("<tr />");
                    $("#table-content").append(row);
                    $.each(row_in_json_table, function(key_in_json_row, cell_in_json_table){
                        row.append($("<td>" + cell_in_json_table + "</td>"));
                    });
                })
            },
            error : function(xhr,errmsg,err) {
                console.log("error")
            }
        });

        $("#files-list").val('');
    });
});