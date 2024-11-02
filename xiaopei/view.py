# -*- coding: utf-8 -*-
 
from django.shortcuts import render
from datetime import datetime
from datetime import datetime

today = datetime.today()

def home_page(request):
    return render(request, 'homepage.html')
