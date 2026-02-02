from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0003_productreview'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='removal_requested',
            field=models.BooleanField(default=False),
        ),
    ]

