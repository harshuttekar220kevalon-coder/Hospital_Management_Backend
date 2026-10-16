import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Receptionist', '0002_receptionistnotification_delete_notification_and_more'),
        ('Super_Admin', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name='ReceptionistChat',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('sender_name', models.CharField(max_length=150)),
                        ('sender_email', models.EmailField(db_index=True, max_length=254)),
                        ('sender_role', models.CharField(db_index=True, max_length=50)),
                        ('recipient_name', models.CharField(blank=True, default='', max_length=150)),
                        ('recipient_email', models.CharField(db_index=True, max_length=254)),
                        ('recipient_role', models.CharField(db_index=True, max_length=50)),
                        ('message', models.TextField()),
                        ('is_broadcast', models.BooleanField(db_index=True, default=False)),
                        ('is_read', models.BooleanField(db_index=True, default=False)),
                        ('read_at', models.DateTimeField(blank=True, null=True)),
                        ('hospital_name', models.CharField(blank=True, default='', max_length=150)),
                        ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('hospital', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receptionist_chats', to='Super_Admin.hospitals')),
                    ],
                    options={
                        'db_table': 'Receptionist_receptionistchat',
                        'ordering': ['created_at', 'id'],
                    },
                ),
            ],
        ),
    ]
