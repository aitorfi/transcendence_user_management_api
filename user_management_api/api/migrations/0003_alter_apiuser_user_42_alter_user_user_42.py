# Generated by Django 5.1.1 on 2024-10-02 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_apiuser_friends_blocked_apiuser_user_42_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apiuser',
            name='user_42',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_42',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
