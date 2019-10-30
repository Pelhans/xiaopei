# -*- coding: utf-8 -*-

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from ..models import Question
from ..models import Question_audio
import os

import json
import socket
import struct

serverIp = '0.0.0.0'; #问答模块网络ip地址
serverPort = 8086; #问答模块网络端口
addr = (serverIp, serverPort);

def answer(quetion):
    addr = (serverIp, serverPort);
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    sock.connect(addr);
    print("Watting for response.....")
    send = quetion;
    sock.send(send);  # 发送信息
    answer = sock.recv(1024)
    return answer

@api_view(['POST'])
def deal_question( request ):
    result = {}
    requestData = json.loads(request.body)
    question = requestData['talkwords']
    result["message"] = answer(question)

    result["statusCode"] = 200
    return Response(result,status=status.HTTP_200_OK)

