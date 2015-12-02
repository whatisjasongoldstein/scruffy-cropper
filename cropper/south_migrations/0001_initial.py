# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Crop'
        db.create_table('cropper_crop', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('field', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('coordinations', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('cropper', ['Crop'])


    def backwards(self, orm):
        # Deleting model 'Crop'
        db.delete_table('cropper_crop')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'cropper.crop': {
            'Meta': {'object_name': 'Crop'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'coordinations': ('django.db.models.fields.TextField', [], {}),
            'field': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['cropper']