# Generated by Django 3.1.5 on 2021-03-01 16:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0006_auto_20210228_1221'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Follower',
            new_name='Follow',
        ),
    ]
