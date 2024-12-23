
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render, HttpResponse, redirect

class LoadingMiddleware(MiddlewareMixin):

    def __init__(self, get_response):  # �� Django ����ʱ���ã�ͨ�����ڳ�ʼ���м��
        super().__init__(get_response)
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        return response

    def process_request(self, request):
        pass