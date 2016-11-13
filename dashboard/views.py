# -*- coding: utf-8 -*-
import logging as log

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_GET

from clients.models import Clients, NodeInfo


def do_login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse('home'))
        else:
            return render(request, 'login.html', context=dict(auth_failed=True))


def do_logout(request):
    logout(request)
    return redirect(reverse('login'))


def get_client_list(request):
    try:
        page = int(request.GET.get('page', 1))
        rows = int(request.GET.get('rows', 10))
    except Exception as e:
        log.error('got an page error: %s' % e)
        page = 1
        rows = 10

    all_clients = Clients.get_all_clients()

    try:
        p = Paginator(all_clients, rows)
        cur_page = p.page(page)
    except Exception as e:
        log.error('got an error: %s' % e)
        raise

    node_ids = [i.nodeid for i in cur_page.object_list]
    node_info_mapping = NodeInfo.get_node_info_mapping(node_ids)

    records = []
    for obj in cur_page.object_list:
        node_info = node_info_mapping[obj.nodeid]
        label = node_info.label if node_info else ''
        records.append({
            'id': obj.id,
            'nodeid': obj.nodeid,
            'addr': obj.addr,
            'from_field': obj.from_field,
            'model': obj.model,
            'rssi': obj.rssi,
            'ssid': obj.ssid,
            'action': obj.action,
            'timestamp': obj.timestamp,
            'time': obj.time,
            'label': label,
        })

    return JsonResponse({'records': p.count, 'rows': records, 'page': page, 'total': p.num_pages})


def update_node_info(request):
    nodeid = request.POST.get('nodeid', '')
    label = request.POST.get('label', '').strip()
    if not nodeid:
        return JsonResponse({'success': False, 'error': 'invalid nodeid'})

    nodeinfo, _ = NodeInfo.get_or_create(nodeid)
    if nodeinfo:
        nodeinfo.label = label
        nodeinfo.save()

    return JsonResponse({'success': True})


@login_required
def client_list(request):
    if request.method == 'POST':
        return update_node_info(request)
    else:
        return get_client_list(request)


@require_GET
@login_required
def node_list(request):
    node_ids = Clients.get_unique_node_ids()
    node_info_mapping = NodeInfo.get_node_info_mapping(node_ids)
    result = []
    for node_id in sorted(node_ids):
        node_info = node_info_mapping[node_id]
        label = node_info.label if node_info else ''
        result.append({
            'node_id': node_id,
            'label': label,
        })
    return JsonResponse({'node_ids': result})
