from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0002_userplanselection_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userplanselection',
            name='activated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]