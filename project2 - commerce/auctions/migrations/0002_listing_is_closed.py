# Generated by Django 3.2.7 on 2022-11-11 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='is_closed',
            field=models.BooleanField(default=False),
        ),
    ]
