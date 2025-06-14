# Generated by Django 5.0.2 on 2025-04-14 06:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='inventoryitem',
            options={'ordering': ['-created_at'], 'verbose_name': 'Inventory Item', 'verbose_name_plural': 'Inventory Items'},
        ),
        migrations.RemoveField(
            model_name='agent',
            name='contact_info',
        ),
        migrations.RemoveField(
            model_name='agent',
            name='record_origin',
        ),
        migrations.RemoveField(
            model_name='inventoryitem',
            name='in_use_quantity',
        ),
        migrations.RemoveField(
            model_name='inventoryitem',
            name='total_quantity',
        ),
        migrations.AddField(
            model_name='agent',
            name='contact_number',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AddField(
            model_name='agent',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='quantity',
            field=models.PositiveIntegerField(default=0, help_text='Total quantity of items'),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='unit_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='agent',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='available_quantity',
            field=models.PositiveIntegerField(default=0, help_text='Quantity available for assignment'),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='category',
            field=models.CharField(choices=[('furniture', 'Furniture'), ('electronics', 'Electronics'), ('appliances', 'Appliances'), ('tools', 'Tools'), ('other', 'Other')], default='other', max_length=20),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agent_name', models.CharField(max_length=100)),
                ('quantity', models.PositiveIntegerField()),
                ('assigned_date', models.DateTimeField(auto_now_add=True)),
                ('return_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('assigned', 'Assigned'), ('returned', 'Returned'), ('lost', 'Lost'), ('damaged', 'Damaged')], default='assigned', max_length=20)),
                ('remarks', models.TextField(blank=True)),
                ('inventory_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='core.inventoryitem')),
            ],
        ),
        migrations.DeleteModel(
            name='AssignmentRecord',
        ),
    ]
