# Generated by Django 3.2 on 2025-05-14 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_complain_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complain',
            name='status',
            field=models.CharField(choices=[('Initiated', 'Initiated'), ('In_Progress', 'In Progress'), ('Resolved', 'Resolved')], default='initiated', max_length=20),
        ),
    ]
