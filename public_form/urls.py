from django.conf.urls import *
from public_form.views import entry_page_to_gestioci, create_membership, wait_membership, activate_membership, save_form_profile, save_form_self_employed

urlpatterns = patterns('',
	url(r'^(?P<record_type_id>\d+)/$',
	   create_membership,
	   name='create_membership'),
	url(r'^$',
	   create_membership,
	   name='create_membership'),
	url(r'^wait/(?P<user_id>\w+)/$',
	   wait_membership,
	   name='wait_membership'),
	url(r'^activate/(?P<activation_key>\w+)/$',
	   activate_membership,
	   name='activate_membership'),
	url(r'^entry_page_to_gestioci/(?P<user_id>\d+)/$',
	   entry_page_to_gestioci,
	   name='entry_page_to_gestioci'),
	url(r'^entry_page_to_gestioci/$',
	   entry_page_to_gestioci,
	   name='entry_page_to_gestioci'),
	url(r'^save_form_profile/$',
	   save_form_profile,
	   name='save_form_profile'),
	url(r'^save_form_self_employed/$',
	   save_form_self_employed,
	   name='save_form_self_employed'),
	)

