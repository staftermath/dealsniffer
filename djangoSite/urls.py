"""djangoSite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import auth
from django.contrib import admin
from djangoSite import views
# from access.views import view_user_deal

urlpatterns = [
    url('^', include('django.contrib.auth.urls'), name='login'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^profile/', views.profile, name='profile'),
    url(r'^logged_out/$', views.logout_user, name='loggedout'),
    url(r'^$', views.index, name='homepage'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^chart/$', views.dealtrend, name='dealtrend'),
    url(r'^parser/$', views.addparser, name='parser'),
    url(r'^api/plottrend/$', views.plottrend, name='api_plottrend'),
    url(r'^api/getdeal/$', views.generate_deal_data, name='api_getdeal'),
    url(r'^api/getdealforthisparser/$', views.get_deal_for_parser, name='api_deal_for_parser'),
    # url(r'^user_deal/$', view_user_deal, name='view_user_deal'),
]
