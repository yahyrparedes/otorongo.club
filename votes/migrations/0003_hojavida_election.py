# Generated by Django 3.1.4 on 2020-12-26 20:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0002_auto_20201226_1948'),
    ]

    operations = [
        migrations.AddField(
            model_name='hojavida',
            name='election',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='votes.elections'),
        ),
    ]
