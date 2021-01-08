# Generated by Django 3.1.4 on 2021-01-08 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0011_auto_20210107_2035'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='chinese_name',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='korean_name',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='english_name',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]