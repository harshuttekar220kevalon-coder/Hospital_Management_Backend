from django.db import migrations


def create_doctorchat_table(apps, schema_editor):
    DoctorChat = apps.get_model("Doctor", "DoctorChat")
    table_name = DoctorChat._meta.db_table
    existing_tables = schema_editor.connection.introspection.table_names()

    if table_name not in existing_tables:
        schema_editor.create_model(DoctorChat)


class Migration(migrations.Migration):
    dependencies = [
        ("Doctor", "0004_alter_doctor_consultation_fee_and_more"),
    ]

    operations = [
        migrations.RunPython(
            create_doctorchat_table,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
