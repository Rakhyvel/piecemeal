# Generated by Django 5.2.3 on 2025-07-04 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('piecemeal_app', '0005_plannedmeal'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plannedmeal',
            name='date',
        ),
        migrations.AddField(
            model_name='plannedmeal',
            name='day',
            field=models.CharField(choices=[('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'), ('sunday', 'Sunday')], default='monday', max_length=10),
            preserve_default=False,
        ),
    ]
