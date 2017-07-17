from django.db import models


class UploadedFiles(models.Model):
    class Meta:
        db_table = 'uploaded_files'
    unique_file_name = models.CharField(max_length = 50, primary_key = True)
    absolut_file_path = models.CharField(max_length = 500, unique = True, db_index = True)
    original_file_name = models.CharField(max_length = 500)
    upload_into_es_task_id = models.CharField(max_length = 50, unique = True, null = True, db_index = True)
    upload_into_es_rows_count = models.PositiveIntegerField(null = True)
    upload_into_es_cols_count = models.PositiveIntegerField(null = True)
    upload_into_es_file_size = models.PositiveIntegerField(null = True)
    upload_into_es_settings_rcs = models.PositiveSmallIntegerField(null = True)
    upload_into_es_settings_pp = models.PositiveSmallIntegerField(null = True)
    upload_into_es_settings_ics = models.PositiveSmallIntegerField(null = True)
    upload_into_es_ttm = models.FloatField(null = True)
    upload_into_es_itm = models.FloatField(null=True)

