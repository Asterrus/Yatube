# Generated by Django 2.2.16 on 2022-11-20 18:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0018_auto_20221120_2119'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='UniqueFollow',
        ),
    ]
