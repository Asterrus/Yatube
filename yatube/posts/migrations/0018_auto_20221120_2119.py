# Generated by Django 2.2.16 on 2022-11-20 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0017_auto_20221120_1913'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='UniqueFollow'),
        ),
    ]
