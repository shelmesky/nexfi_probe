# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import defaultdict

from django.db import models


class Clients(models.Model):
    nodeid = models.CharField(max_length=128)
    addr = models.CharField(max_length=128)
    from_field = models.CharField(db_column='from', max_length=128)
    model = models.CharField(max_length=128)
    rssi = models.IntegerField()
    ssid = models.CharField(max_length=128, blank=True, null=True)
    action = models.IntegerField(blank=True, null=True)
    timestamp = models.IntegerField()
    time = models.CharField(max_length=128)

    class Meta:
        managed = False
        db_table = 'clients'

    @classmethod
    def get_unique_node_ids(cls):
        return list(cls.objects.values_list('nodeid', flat=True).annotate().distinct())

    @classmethod
    def get_all_clients(cls):
        return cls.objects.order_by('-id').all()


class NodeInfo(models.Model):
    nodeid = models.CharField(max_length=128, unique=True)
    label = models.CharField(max_length=128)

    @classmethod
    def get_node_info_mapping(cls, node_ids):
        info = cls.objects.filter(nodeid__in=node_ids)
        result = defaultdict(lambda: None)
        for i in info:
            result[i.nodeid] = i

        return result

    @classmethod
    def get_or_create(cls, nodeid):
        return cls.objects.get_or_create(nodeid=nodeid)
