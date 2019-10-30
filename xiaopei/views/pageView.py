# -*- coding: utf-8 -*-
 
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from django.core import serializers
from ..models import User, Meeting,Question_audio
from django.http import FileResponse
from pydub import AudioSegment
import wave
import socket
import struct
import io
import pyaudio
import json
import os

def getUser(userName):
	try:
		user = User.objects.get(userName=userName);
		if (user is None):
			return {};
		return user;
	except Exception, e:
		return {};

def getMeeting(id):
	try:
		meeting = Meeting.objects.get(id=id);
		if (meeting is None):
			return {};
		return meeting;
	except Exception, e:
		return {};

def index(request):
	data = {};
	message = request.session.get('message', None);
	request.session["message"]="ok";
	if message is None:
		data["message"] = "ok";
	data["message"] = message;
	return render(request, 'answer.html', data)

def reloadUsers(request, id):
	users = User.objects.filter(id=id);
	user = users[0];
	request.session["id"]=user.id;
	request.session["userName"]=user.userName;
	request.session["password"]=user.password;
	request.session["position"]=user.position;
	request.session["email"]=user.email;
	request.session["message"]="ok";
	return getUsersPage(request);

def reloadUser(request, id):
	users = User.objects.filter(id=id);
	user = users[0];
	request.session["id"]=user.id;
	request.session["userName"]=user.userName;
	request.session["password"]=user.password;
	request.session["position"]=user.position;
	request.session["email"]=user.email;
	request.session["message"]="ok";
	return getUserInfo(request);

def getRegisterPage(request):
	return render(request, 'register.html');

def getNewMeetingPage(request):
	userName = request.session.get('userName', None);
	if userName is None:
		return HttpResponseRedirect('/');
	data = {};
	data['activeUser'] = getUser(userName);
	return render(request, 'newMeeting.html',data);

def getUploadMeetingPage(request):
	userName = request.session.get('userName', None);
	if userName is None:
		return HttpResponseRedirect('/');
	data = {};
	data['activeUser'] = getUser(userName);
	return render(request, 'uploadMeeting.html',data);

def getMeetingPage(request, id):
	userName = request.session.get('userName', None);
	if userName is None:
		return HttpResponseRedirect('/');
	data = {};
	data['meeting'] = getMeeting(id);
	data['activeUser'] = getUser(userName);
	return render(request,'record.html', data);

def getUsersPage(request):
	userName = request.session.get('userName', None);
	position = request.session.get('position', None);
	if position is None:
		return HttpResponseRedirect('/');
	if position == "admin":
		users = User.objects.all();
		data = {};
		data['users'] = users;
		data['activeUser'] = getUser(userName);
		return render(request, 'users.html', data);
	return HttpResponseRedirect('/');

def getFilterUsersPage(request,searchName):
	userName = request.session.get('userName', None);
	position = request.session.get('position', None);
	if position is None:
		return HttpResponseRedirect('/');
	if position == "admin":
		users = User.objects.filter(userName=searchName);
		data = {};
		data['users'] = users;
		data['activeUser'] = getUser(userName);
		return render(request, 'users.html', data);
	return HttpResponseRedirect('/');

def getMeetingsPage(request):
	userName = request.session.get('userName', None);
	if userName is None:
		return HttpResponseRedirect('/');
	meetings = Meeting.objects.all();
	data = {};
	data['meetings'] = meetings;
	data['activeUser'] = getUser(userName);
	return render(request, 'meetings.html', data);

def getUserInfo(request):
	userName = request.session.get('userName', None);
	if userName is None:
		return HttpResponseRedirect('/');
	data = {};
	data['activeUser'] = getUser(userName);
	return render(request, 'userInfo.html', data);

def getUploadMeetingPageError(request):
	userName = request.session.get('userName', None);
	if userName is None:
		return HttpResponseRedirect('/');
	data = {};
	data['activeUser'] = getUser(userName);
	data['error'] = "音频错误";
	return render(request, 'uploadMeeting.html',data);

def get_answer(request):

	# 需要把现有的questio返回
	userName=request.session.get('userName',None)
	question_audio = Question_audio.objects.all();
	data = {};
	question = Question_audio()
	question.save()
	print(question.id)
	data['question'] = question
	data['activeUser'] = getUser(userName);
	return render(request,'answer.html', data)
