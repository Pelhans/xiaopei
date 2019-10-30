# -*- coding: utf-8 -*-

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from aip import AipSpeech
from ..models import Question
from ..models import Question_audio
import os

import json
import socket
import struct

serverIp = '0.0.0.0'; #问答模块网络ip地址
serverPort = 8086; #问答模块网络端口
addr = (serverIp, serverPort);

APP_ID = '14247851'
API_KEY = 'pZldi1bBdoCy64BjcUU7Kcxz'
SECRET_KEY = 'CoompVvnVfEYh9HyGjQbcGNM6avIMbtR'

client = AipSpeech(APP_ID,API_KEY,SECRET_KEY)


def answer(quetion):

    addr = (serverIp, serverPort);
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    sock.connect(addr);
    print("Watting for response.....")
    send = quetion;
    sock.send(send);  # 发送信息
    answer = sock.recv(1024)
    return answer

def get_question(talkWord):
    question = Question()
    question.talkWord = talkWord
    return question

@api_view(['POST'])
def deal_question( request ):
    result = {}
    requestData = json.loads(request.body)
    question = requestData['talkwords']
    result["message"] = answer(question)

    result1 = client.synthesis(result["message"], 'zh', 1, {'vol': 5, })

    if not isinstance(result1, dict):
        with open('./static/2.ogg', 'wb') as f:
            f.write(result1)

    result["statusCode"] = 200
    return Response(result,status=status.HTTP_200_OK)

@api_view(['POST'])
def save_record(request, id):
    result = {};
    question = Question_audio.objects.get(id=id);
    if request.method == 'POST':

        file = (request.FILES.getlist('file'))[0];
        baseDir = os.path.dirname(os.path.abspath(__name__));

    wavdir = os.path.join(baseDir,'static','chatwav');
    fwav = open(wavdir + "/" + str(id) + ".wav",'wb');
    for chrunk in file.chunks():
        fwav.write(chrunk);
    fwav.close();
    question.audioUrl = "/download/wav1/" + str(id) + "/"
    question.save();
    print(id)
    result['statusCode'] = 200;
    result["message"] = "ok";
    result['id'] = id
    return Response(result,status=status.HTTP_200_OK);

def downloadWav(request, id):

    result = {}
    baseDir = os.path.dirname(os.path.abspath(__name__));
    wavdir = os.path.join(baseDir,'static','chatwav');
    file=open(wavdir + "/" + str(id) + ".wav",'rb');
    response =HttpResponse(file);
    try:
        question_audio = Question_audio.objects.get(id=id);
        if (question_audio is None):
            result['statusCode'] = 404;
            result["message"] = "not find";
        response['Content-Type']='application/octet-stream';
        wavname = ((question_audio.wavname).encode("utf-8"))
        response['Content-Disposition']='attachment;filename="'+ (wavname + '.wav' + '"');
        return response
    except Exception, e:
        print e
    return response
