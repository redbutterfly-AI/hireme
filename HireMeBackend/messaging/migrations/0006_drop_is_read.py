from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('messaging', '0005_drop_is_read'),
    ]
    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE messaging_message DROP COLUMN IF EXISTS is_read;",
            reverse_sql="ALTER TABLE messaging_message ADD COLUMN is_read boolean NOT NULL DEFAULT false;",
        ),
    ]
