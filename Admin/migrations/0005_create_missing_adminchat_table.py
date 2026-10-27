from django.db import migrations


def create_adminchat_table(apps, schema_editor):
    AdminChat = apps.get_model("Admin", "AdminChat")
    table_name = AdminChat._meta.db_table
    existing_tables = schema_editor.connection.introspection.table_names()

    if table_name not in existing_tables:
        schema_editor.create_model(AdminChat)


class Migration(migrations.Migration):
    dependencies = [
        ("Admin", "0004_alter_hospitaladmin_designation"),
    ]

    operations = [
        migrations.RunPython(
            create_adminchat_table,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
