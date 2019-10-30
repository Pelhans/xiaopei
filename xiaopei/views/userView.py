# -*- coding: utf-8 -*-
 
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from django.core import serializers
from ..models import User, Meeting
from django.http import FileResponse
from pydub import AudioSegment
import wave
import socket
import pageView as pview
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
		
#def login(request):#登入
#	userName = request.POST.get('userName');
#	password = request.POST.get('password');
#	try :
#		user = User.objects.get(userName=userName);
#		if (user is None):
#			request.session["message"]="用户不存在";
#			return HttpResponseRedirect('/');
#		if (user.password == password):#判断密码正确
#			request.session["id"]=user.id;
#			request.session["userName"]=userName;
#			request.session["password"]=password;
#			request.session["position"]=user.position;
#			request.session["email"]=user.email;
#			request.session["message"]="ok";
#			meetings = Meeting.objects.all();#返回所有的meeting
#			return HttpResponseRedirect('/page/meetings/');
#			#data = {};
#			#data['meetings'] = meetings;
#			#data['activeUser'] = user;
#			#return render(request, 'meetings.html', data);
#		request.session["message"]="密码错误";
#		return HttpResponseRedirect('/');
#	except Exception, e :
#		print(e);
#	request.session["message"]="用户不存在";
#	return HttpResponseRedirect('/');

def logout(request):#登出
	del request.session["id"];
	del request.session["userName"];
	del request.session["password"];
	del request.session["position"];
	del request.session["email"];
	del request.session["message"];
	return HttpResponseRedirect('/');

def register(request):#注册
	userName = request.POST.get('userName');
	password = request.POST.get('password');
	email = request.POST.get('email');
	position = "user";
	try:
		user = User.objects.get(userName=userName);
		return HttpResponseRedirect('/page/register/');
	except Exception, e:
		user = User();
		user.userName = userName;
		user.password = password;
		user.email = email;
		user.position = position;
		user.save();
		return HttpResponseRedirect('/');

def resetS(request,id):
	try:
		user = User.objects.get(id=id);
		request.session["id"]=user.id;
		request.session["userName"]=user.userName;
		request.session["password"]=user.password;
		request.session["position"]=user.position;
		request.session["email"]=user.email;
		request.session["message"]="ok";
	except Exception, e:
		print e
	return HttpResponse('ok');

def updateUser(request):#更新用户
	id = request.session.get('id', None);#用户id
	if id is None:
		return HttpResponseRedirect('/');
	if id == (int)(request.POST.get('id', None).encode("utf-8")):
		userName = request.POST.get('userName', None);
		password = request.POST.get('password', None);
		email = request.POST.get('email', None);
		print email
		try:
			user = User.objects.get(id=id);
			print userName;
			print request.session["userName"];
			if userName != request.session["userName"]:
				try:
					test = User.objects.get(userName=userName);
					return pview.getUserInfo(request);
				except Exception, e:
					print e;
			user.userName = userName;
			user.password = password;
			user.email = email;
			user.save();
			request.session["userName"]=userName;
			request.session["password"]=password;
			request.session["email"]=email;
			return pview.getUserInfo(request);
		except Exception, e:
			print e;
	return pview.getUserInfo(request);

def deleteUser(request, id):#根据用户id删除用户
	userName = request.session.get('userName', None);
	position = request.session.get('position', None);
	if position is None:
		return HttpResponseRedirect('/');
	if position == "admin":
		User.objects.filter(id=id).delete();
		users = User.objects.all();
	return pview.getUsersPage(request);

def getUserObject(user):#获取用户的资源类
	objectUser = {};
	objectUser['id'] = user.id;
	objectUser['userName'] = user.userName;
	objectUser['password'] = user.password;
	objectUser['position'] = user.position;
	objectUser['email'] = user.email;
	return objectUser;

def judgePermission(userName, password):#判断用户权限
	try :
		user = User.objects.get(userName=userName);
		if (user is None):
			return 404;
		if (user.password != password):
			return 401;
		return 200;
	except Exception, e :
		return 404;

@api_view(['POST'])
def openGetUser(request):#获取用户信息
	result = {};
	requestData = json.loads(request.body)
	userName = requestData['userName'];
	password = requestData['password'];
	try :
		user = User.objects.get(userName=userName);#获取用户信息
		if (user is None):
			result["statusCode"] = 404;
			result["message"] = "用户不存在";
			return Response(result,status=status.HTTP_200_OK);
		if (user.password != password):#判断密码是否正确
			result["statusCode"] = 401;
			result["message"] = "密码错误";
			return Response(result,status=status.HTTP_200_OK);
		result["statusCode"] = 200;
		result["message"] = "ok";
		result["user"] = getUserObject(user);
		return Response(result,status=status.HTTP_200_OK);
	except Exception, e :
		result["statusCode"] = 404;
		result["message"] = "用户不存在";
		return Response(result,status=status.HTTP_200_OK);

@api_view(['POST'])
def openGetUsers(request):#获取全部用户
	result = {};
	requestData = json.loads(request.body)
	userName = requestData['userName'];
	password = requestData['password'];
	try :
		user = User.objects.get(userName=userName);#判断是否为管理员
		if (user is None):
			result["statusCode"] = 404;
			result["message"] = "用户不存在";
			return Response(result,status=status.HTTP_200_OK);
		if (user.password != password):
			result["statusCode"] = 401;
			result["message"] = "鉴权失败";
			return Response(result,status=status.HTTP_200_OK);
		if (user.position != "admin"):
			result["statusCode"] = 401;
			result["message"] = "权限不足";
			return Response(result,status=status.HTTP_200_OK);
		result["statusCode"] = 200;
		result["message"] = "ok";
		users = User.objects.all();
		userList = [];
		for user in users:
			userList.append(getUserObject(user));
		result["users"] = userList;
		return Response(result,status=status.HTTP_200_OK);
	except Exception, e :
		result["statusCode"] = 404;
		result["message"] = "用户不存在";
		return Response(result,status=status.HTTP_200_OK);

@api_view(['POST'])
def openDeleteUser(request):#删除用户
	result = {};
	requestData = json.loads(request.body)
	userName = requestData['userName'];
	password = requestData['password'];
	deleteUserName = requestData['deleteUserName'];#删除用户
	try :
		user = User.objects.get(userName=userName);
		if (user is None):
			result["statusCode"] = 404;
			result["message"] = "用户不存在";
			return Response(result,status=status.HTTP_200_OK);
		if (user.password != password):
			result["statusCode"] = 401;
			result["message"] = "鉴权失败";
			return Response(result,status=status.HTTP_200_OK);
		if (user.position != "admin"):
			result["statusCode"] = 401;
			result["message"] = "权限不足";
			return Response(result,status=status.HTTP_200_OK);
	except Exception, e :
		result["statusCode"] = 404;
		result["message"] = "用户不存在";
		return Response(result,status=status.HTTP_200_OK);
	try :
		user = User.objects.get(userName=deleteUserName);
		if (user.position == "admin"):
			result["statusCode"] = 401;
			result["message"] = "权限不足";
			return Response(result,status=status.HTTP_200_OK);
		user.delete();
		result["statusCode"] = 200;
		result["message"] = "ok";
		return Response(result,status=status.HTTP_200_OK);
	except Exception, e :
		result["statusCode"] = 404;
		result["message"] = "被删除用户不存在";
		return Response(result,status=status.HTTP_200_OK);

@api_view(['POST'])
def openDeleteUsers(request):#删除一批用户
	result = {};
	requestData = json.loads(request.body)
	userName = requestData['userName'];
	password = requestData['password'];
	deleteUsersName = requestData['deleteUsersName'];#需要删除的用户名们
	try :
		user = User.objects.get(userName=userName);
		if (user is None):
			result["statusCode"] = 404;
			result["message"] = "用户不存在";
			return Response(result,status=status.HTTP_200_OK);
		if (user.password != password):
			result["statusCode"] = 401;
			result["message"] = "鉴权失败";
			return Response(result,status=status.HTTP_200_OK);
		if (user.position != "admin"):
			result["statusCode"] = 401;
			result["message"] = "权限不足";
			return Response(result,status=status.HTTP_200_OK);
	except Exception, e :
		result["statusCode"] = 404;
		result["message"] = "用户不存在";
		return Response(result,status=status.HTTP_200_OK);
	for deleteUserName in deleteUsersName:
		try :
			user = User.objects.get(userName=deleteUserName);
			if (user.position == "admin"):
				continue;
			user.delete();
		except Exception, e :
			print e
	result["statusCode"] = 200;
	result["message"] = "ok";
	return Response(result,status=status.HTTP_200_OK);

@api_view(['POST'])
def openSearchUser(request): #搜索用户
	result = {};
	requestData = json.loads(request.body)
	userName = requestData['userName'];
	password = requestData['password'];
	searchUserName = requestData['searchUserName'];#需要搜索的用户名
	try :
		user = User.objects.get(userName=userName);
		if (user is None):
			result["statusCode"] = 404;
			result["message"] = "用户不存在";
			return Response(result,status=status.HTTP_200_OK);
		if (user.password != password):
			result["statusCode"] = 401;
			result["message"] = "鉴权失败";
			return Response(result,status=status.HTTP_200_OK);
		if (user.position != "admin"):
			result["statusCode"] = 401;
			result["message"] = "权限不足";
			return Response(result,status=status.HTTP_200_OK);
	except Exception, e :
		result["statusCode"] = 404;
		result["message"] = "用户不存在";
		return Response(result,status=status.HTTP_200_OK);
	users = User.objects.filter(userName=searchUserName);
	if len(users) >= 1:
		result['user'] = getUserObject(users[0]);
	else :
		result["statusCode"] = 404;
		result["message"] = "用户不存在";
		return Response(result,status=status.HTTP_200_OK);
	result["statusCode"] = 200;
	result["message"] = "ok";
	return Response(result,status=status.HTTP_200_OK);

@api_view(['POST'])
def openSearchUserID(request):#根据用户id 查询用户
	result = {};
	requestData = json.loads(request.body)
	userName = requestData['userName'];
	password = requestData['password'];
	searchID = requestData['searchID'];
	try :
		user = User.objects.get(userName=userName);#查询用户信息
		if (user is None):
			result["statusCode"] = 404;
			result["message"] = "用户不存在";
			return Response(result,status=status.HTTP_200_OK);
		if (user.password != password):
			result["statusCode"] = 401;
			result["message"] = "鉴权失败";
			return Response(result,status=status.HTTP_200_OK);
		if (user.position != "admin"):
			result["statusCode"] = 401;
			result["message"] = "权限不足";
			return Response(result,status=status.HTTP_200_OK);
	except Exception, e :
		result["statusCode"] = 404;
		result["message"] = "用户不存在";
		return Response(result,status=status.HTTP_200_OK);
	users = User.objects.filter(id=searchID);
	if len(users) >= 1:
		result['user'] = getUserObject(users[0]);
	else :
		result["statusCode"] = 404;
		result["message"] = "用户不存在";
		return Response(result,status=status.HTTP_200_OK);
	result["statusCode"] = 200;
	result["message"] = "ok";
	return Response(result,status=status.HTTP_200_OK);

@api_view(['POST'])
def openRegister(request): #注册新用户
	result = {};
	requestData = json.loads(request.body)
	userName = requestData['userName'];
	password = requestData['password'];
	email = requestData['email'];
	try :
		user = User.objects.get(userName=userName); #判断用户是否存在
	except Exception, e :
		user = User();
		user.userName = userName;
		user.password = password;
		user.email = email;
		position = "user";
		user.save();
		result["user"] = getUserObject(user);
		result["statusCode"] = 200;
		result["message"] = "ok";
		return Response(result,status=status.HTTP_200_OK);
	result["statusCode"] = 400;
	result["message"] = "用户已存在";
	return Response(result, status=status.HTTP_200_OK);

@api_view(['POST'])
def openUpdateUser(request): #更新用户信息
	result = {};
	requestData = json.loads(request.body)
	id = requestData['id'];
	userName = requestData['userName'];
	oldPassword = requestData['oldPassword'];#旧密码
	newPassword = requestData['newPassword'];#新密码
	email = requestData['email'];
	try :
		user = User.objects.get(id=id);#获取用户
		if (user is None):
			result["statusCode"] = 404;
			result["message"] = "用户不存在";
			return Response(result,status=status.HTTP_200_OK);
		if (user.password != oldPassword): #判断密码是否正确
			result["statusCode"] = 401;
			result["message"] = "密码错误";
			return Response(result,status=status.HTTP_200_OK);
		if (user.userName != userName):
			try:
				test = User.objects.get(userName=userName);
				result["statusCode"] = 400;
				result["message"] = "用户已存在";
				return Response(result,status=status.HTTP_200_OK);
			except Exception, e :
				print e;
		result["message"] = "";
		if (user.userName != userName):
			user.userName = userName;
			result["message"] = "用户名已更新;";
		if (user.password != newPassword):
			user.password = newPassword;
			result["message"] = result["message"] + "用户密码已更新";
		if (user.email != email):
			user.email = email;
			result["message"] = result["message"] + "用户邮箱已更新";
		user.save();
		result["statusCode"] = 200;
		if result["message"] == "":
			result["message"] = "无更新";
		return Response(result,status=status.HTTP_200_OK);
	except Exception, e :
		result["statusCode"] = 404;
		result["message"] = "用户不存在";
		return Response(result,status=status.HTTP_200_OK);

@api_view(['POST'])
def openAdminUpdateUser(request): #管理员更新用户信息
	result = {};
	requestData = json.loads(request.body)
	userName = requestData['userName'];
	password = requestData['password'];
	updateID = requestData['updateID'];
	updateUserName = requestData['updateUserName'];
	updatePassword = requestData['updatePassword'];
	updateEmail = requestData['updateEmail'];
	try :
		user = User.objects.get(userName=userName); #查询用户 看是否为管理员
		if (user is None):
			result["statusCode"] = 404;
			result["message"] = "用户不存在"; 
			return Response(result,status=status.HTTP_200_OK);
		if (user.password != password):
			result["statusCode"] = 401;
			result["message"] = "密码错误";
			return Response(result,status=status.HTTP_200_OK);
		if (user.position != "admin"):
			result["statusCode"] = 401;
			result["message"] = "权限不足";
			return Response(result,status=status.HTTP_200_OK);
	except Exception, e :
		result["statusCode"] = 404;
		result["message"] = "用户不存在";
		return Response(result,status=status.HTTP_200_OK);
	try :
		user = User.objects.get(id=updateID); #查询被更改的用户
		if (user is None):
			result["statusCode"] = 404;
			result["message"] = "更新用户不存在";
			return Response(result,status=status.HTTP_200_OK);
		if updateUserName != user.userName:
			try :
				test = User.objects.get(userName=updateUserName); #查询用户是否存在
				result["statusCode"] = 400;
				result["message"] = "用户已经存在";
				return Response(result,status=status.HTTP_200_OK);
			except Exception, e :
				print e;
		result["message"] = "";
		if (user.userName != updateUserName):
			user.userName = updateUserName;
			result["message"] = "用户名已更新;";
		if (user.password != updatePassword):
			user.password = updatePassword;
			result["message"] = result["message"] + "用户密码已更新";
		if (user.email != updateEmail):
			user.email = updateEmail;
			result["message"] = result["message"] + "用户邮箱已更新";
		user.save(); 
		result["statusCode"] = 200;
		if result["message"] == "":
			result["message"] = "无更新";
		return Response(result,status=status.HTTP_200_OK);
	except Exception, e :
		result["statusCode"] = 404;
		result["message"] = "更新用户不存在";
		return Response(result,status=status.HTTP_200_OK);
