from django.db import migrations


def create_receptionistchat_table(apps, schema_editor):
    ReceptionistChat = apps.get_model("Receptionist", "ReceptionistChat")
    table_name = ReceptionistChat._meta.db_table
    existing_tables = schema_editor.connection.introspection.table_names()

    if table_name not in existing_tables:
        schema_editor.create_model(ReceptionistChat)


class Migration(migrations.Migration):
    dependencies = [
        ("Receptionist", "0004_alter_receptionist_languages_and_more"),
    ]

    operations = [
        migrations.RunPython(
            create_receptionistchat_table,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
