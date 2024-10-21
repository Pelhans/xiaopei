# -*- coding: utf-8 -*-
 
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from datetime import datetime
from django.core import serializers
from .models import User, Chatting
from django.core.files.storage import FileSystemStorage
from .forms import UploadFileForm
from . import process_sbs_parse
from django.http import FileResponse
import socket
import struct
import io
import json
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging
import requests
import time

import hmac
import base64
import requests
import time
import json
import re
from hashlib import sha256

from typing import Dict
from collections import defaultdict

today = datetime.today()

def home_page(request):
    return render(request, 'homepage.html')

def handle_uploaded_file(f):
    upload_dir = 'uploads/'
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    file_path = os.path.join(upload_dir, f.name)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path

def upload_sbs_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_path = handle_uploaded_file(request.FILES['file'])
            # 调用解析函数
            parsed_file_path = process_sbs_parse.parse(file_path)
            # parsed_file_path = file_path
            with open(parsed_file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type="application/octet-stream")
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(parsed_file_path)}"'
                return response
    else:
        form = UploadFileForm()
    return render(request, 'homepage.html', {'form': form})
