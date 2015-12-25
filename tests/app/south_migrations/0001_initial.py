# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Office'
        db.create_table(u'app_office', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('office', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'app', ['Office'])

        # Adding model 'Tag'
        db.create_table(u'app_tag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'app', ['Tag'])

        # Adding model 'Person'
        db.create_table(u'app_person', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('name_de', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('surname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('surname_de', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('surname_en', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('security_level', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('some_excluded_field', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=3)),
            ('office', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Office'], null=True, blank=True)),
        ))
        db.send_create_signal(u'app', ['Person'])

        # Adding M2M table for field tags on 'Person'
        m2m_table_name = db.shorten_name(u'app_person_tags')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('person', models.ForeignKey(orm[u'app.person'], null=False)),
            ('tag', models.ForeignKey(orm[u'app.tag'], null=False))
        ))
        db.create_unique(m2m_table_name, ['person_id', 'tag_id'])


    def backwards(self, orm):
        # Deleting model 'Office'
        db.delete_table(u'app_office')

        # Deleting model 'Tag'
        db.delete_table(u'app_tag')

        # Deleting model 'Person'
        db.delete_table(u'app_person')

        # Removing M2M table for field tags on 'Person'
        db.delete_table(db.shorten_name(u'app_person_tags'))


    models = {
        u'app.office': {
            'Meta': {'object_name': 'Office'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'office': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'app.person': {
            'Meta': {'object_name': 'Person'},
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name_de': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'office': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app.Office']", 'null': 'True', 'blank': 'True'}),
            'security_level': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'some_excluded_field': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '3'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'surname_de': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'surname_en': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['app.Tag']", 'symmetrical': 'False'})
        },
        u'app.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['app']