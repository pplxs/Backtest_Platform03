
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render, HttpResponse, redirect

class LoadingMiddleware(MiddlewareMixin):

    def __init__(self, get_response):  # 当 Django 启动时调用，通常用于初始化中间件
        super().__init__(get_response)
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        return response

    def process_request(self, request):
        pass