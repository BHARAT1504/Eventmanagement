# Generated by Django 5.0.3 on 2024-04-19 05:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventapi', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NonRegisteredRSVP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eventapi.event')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eventapi.role')),
            ],
        ),
    ]
