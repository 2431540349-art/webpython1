from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mockquestion',
            name='sample_answer',
            field=models.TextField(blank=True, help_text='Sample answer text for speaking questions. Used for speech recognition comparison.', null=True),
        ),
    ]