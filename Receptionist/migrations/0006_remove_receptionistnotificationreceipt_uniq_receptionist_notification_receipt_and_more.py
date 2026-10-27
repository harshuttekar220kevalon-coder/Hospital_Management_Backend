
from django.db import migrations


def safely_remove_receipt_table(apps, schema_editor):
    connection = schema_editor.connection
    table_name = "Receptionist_receptionistnotificationreceipt"

    existing_tables = connection.introspection.table_names()

    if table_name in existing_tables:
        model = apps.get_model("Receptionist", "ReceptionistNotificationReceipt")
        schema_editor.delete_model(model)


class Migration(migrations.Migration):

    dependencies = [
        ("Receptionist", "0005_create_missing_receptionistchat_table"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    safely_remove_receipt_table,
                    migrations.RunPython.noop,
                ),
            ],
            state_operations=[
                migrations.DeleteModel(
                    name="ReceptionistNotificationReceipt",
                ),
            ],
        ),
    ]
