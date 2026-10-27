from django.db import migrations


def create_nursechat_table(apps, schema_editor):
    NurseChat = apps.get_model("Nurse", "NurseChat")
    table_name = NurseChat._meta.db_table
    existing_tables = schema_editor.connection.introspection.table_names()

    if table_name not in existing_tables:
        schema_editor.create_model(NurseChat)


class Migration(migrations.Migration):
    dependencies = [
        ("Nurse", "0004_alter_nurse_nurse_id_alter_nurse_password_and_more"),
    ]

    operations = [
        migrations.RunPython(
            create_nursechat_table,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
