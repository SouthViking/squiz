# Generated by Django 4.2.3 on 2023-08-03 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0006_userselection'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='draft_mode',
            field=models.BooleanField(default=True),
        ),
    ]
