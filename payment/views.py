from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# @method_decorator(cache_page(60 * 5, key_prefix="payment_view"))
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)
