#encoding=utf-8
'''
 1) COMMON IMPORTS
 2) TOOLS
 3) SITE REGISTER
	3.1) Admin
	3.2) Cooper
'''
'''
 1) COMMON IMPORTS
 2) 
 3) 
'''
 #Localization
from django.utils.translation import ugettext_lazy as _
'''
 1) 
 2) TOOLS
 3) 
'''

from django.contrib.admin import SimpleListFilter
#Use this in like => list_filter = (onlyownedFilter,)
class onlyownedFilter(SimpleListFilter):
	# Human-readable title which will be displayed in the
	# right admin sidebar just above the filter options.
    	title = _(u'Hola usuari')

	# Parameter for the filter that will be used in the URL query.
	parameter_name = 'onlyowned'

	def lookups(self, request, model_admin):
		return (
			('Mine', _(u'les meves factures')),
		)

	def queryset(self, request, queryset):
	# Compare the requested value (either '80s' or '90s')
	# to decide how to filter the queryset.
		if self.value() == 'Mine':
			return queryset.filter(user=request.user)

#Use this in a ModelAdmin.list_filter property
class First_Period_Filter (SimpleListFilter):
	title = _(u'primer període')
	parameter_name = 'first_period'

	def lookups(self, request, model_admin):
		qs_periods = period.objects.all()
		yFilters = ()
		for ob_period in qs_periods:
			yFilters = yFilters + ((ob_period.id, ob_period),)
		return yFilters

	def queryset(self, request, queryset):
		if self.value():
			qs_period = period.objects.get( id = self.value() )
			qs = queryset.filter ( cooper__user__date_joined__gt = qs_period.first_day, cooper__user__date_joined__lt = qs_period.date_close )
			return qs

		return queryset

#Use this in a ModelAdmin.list_filter property
class Closing_Filter (SimpleListFilter):
	title = _(u'Resultats (Selecciona avanç un Període)')
	parameter_name = 'closing'

	def lookups(self, request, model_admin):
		return (
			('1', _('Socis que han tancat')),
			('2', _('Socis que han creat el registre pero no han tancat')),
			('3', _('Socis que no han creat el registre')),
		)

	def queryset(self, request, queryset):
		if request.GET.has_key('first_period'):
			id_period = request.GET['first_period']
			if self.value() == '1':
				qs = queryset.filter( cooper__period_close__period_id = id_period, cooper__period_close__closed = True )
				return qs
			if self.value() == '2':
				qs = queryset.filter( cooper__period_close__period_id = id_period, cooper__period_close__closed = False )
				return qs
			if self.value() == '3':
				qs = queryset.exclude( cooper__period_close__period_id = id_period )
				return qs

'''
 1) 
 2) SITE REGISTER
 3) 
'''
#Base entity
from django.contrib.admin import ModelAdmin

# Import models
from Invoices.models import *

# Export csv plugin
from Invoices.action import export_as_csv_action, export_all_as_csv_action

#Use this by registrating of ModelAdmin in admin.site to specific cooper csv import
from django import forms
class CSVImportAdmin(ModelAdmin):
	''' Custom model to not have much editable!'''
	readonly_fields = ['file_name',
					   'upload_method',
					   'error_log_html',
					   'import_user']
	fields = [
				'model_name',
				'field_list',
				'upload_file',
				'file_name',
				'encoding',
				'upload_method',
				'error_log_html',
				'import_user']
	formfield_overrides = {
		models.CharField: {'widget': forms.Textarea(attrs={'rows':'4',
			   'cols':'60'})},
		}

	def save_model(self, request, obj, form, change):
		form.save()
		#TODO: Use a command  from App.management.commands.myCSVimporterLib import Command
		#      cmd = Command()
		if obj.upload_file:
			obj.file_name = obj.upload_file.name
			obj.encoding = ''
			defaults = self.filename_defaults(obj.file_name)
			members = open(settings.MEDIA_BASE + str(obj.upload_file))
			data = csv.DictReader(members)
			default_password = 'tsc_eclub'
			errors = [] 
			error = False
			coopnum = None
			for row in data:
				try:
					name = row['name'][0:29]
					lastname = row['lastname'][0:29]
					email = row['email']
					coop = row['coop']
					coopnum = row['coopnum']
					coopnum=coopnum.replace("COOP","")
					passw = row['password']
					vat = row['iva']
					vat = vat.replace("%","")
					tax = row['tax']
				except:
					errors.append("\n S'han de revisar les columnes")
					error = True
				
				if not error and not coopnum:
					errors.append("\n Falta num cooper")
				
				r_coop= Coop.objects.filter(name=coop)
				if not error and not r_coop:
					errors.append("\n Per %s no trobem la cooperativa %s" % (coopnum, coop))

				if not vat:
					vat = 0
				if not tax:
					tax = 0

				if coopnum and r_coop:
					user = None
					with transaction.atomic():
						try:
							try:
								user = User.objects.get(username = coopnum)
							except:
								print "not existing " + coopnum
								user = None
							
							if user:
								user.first_name = name
								user.last_name = lastname
								user.save()
							else:
								user = User.objects.create_user(coopnum, email, passw)
								user.is_staff = False
								user.first_name = name
								user.last_name = lastname
								user.save()

								if user:
									from django.contrib.auth.models import Group
									g = Group.objects.get(name='cooper') 
									g.user_set.add(user)
									
									cooper = cooper (user=user, coop=r_coop[0], coop_number=coopnum, assigned_vat=vat, advanced_tax=tax)
									cooper.save()
						except IntegrityError as e:
							errors.append("\n" + str(e))
							errors.append("\n" + str(row))
						except Exception as e:
							print e
							print lastname
							print name

			#errors = ["Finalitzat el procés"]
			if errors or error:
				obj.error_log = '\n'.join(errors)

			obj.import_user = str(request.user)
			obj.import_date = datetime.now()
			obj.save()
			

	def filename_defaults(self, filename):
		""" Override this method to supply filename based data """
		defaults = []
		splitters = {'/':-1, '.':0, '_':0}
		for splitter, index in splitters.items():
			if filename.find(splitter)>-1:
				filename = filename.split(splitter)[index]
		return defaults

#GENERATE CONTROL PANEL MENU
'''
3.1) ADMIN
'''
#Add any Invoice new Entity for ADMIN  below:
from django.contrib import admin

from Invoices.bots import *

admin.site.register(vats)
admin.site.register(currencies)

class coop_admin(ModelAdmin):
	fields = ['name', ]
	list_display = ('name', )
	actions = [export_as_csv_action("Exportar CSV", fields=list_display, header=True, force_fields=True),]
admin.site.register(coop, coop_admin)

class tax_admin(ModelAdmin):
	fields = ['value', 'min_base', 'max_base']
	list_display = ('value', 'min_base', 'max_base')
	actions = [export_as_csv_action("Exportar CSV", fields=list_display, header=True, force_fields=True),]
admin.site.register(tax, tax_admin)

class EmailNotificationAdmin(ModelAdmin):
	class Media:
			js = (
				'EmailNotification.js',   # app static folder
			)
	fields = ['efrom', 'eto', 'ento', 'sent_to_user', 'subject', 'body', 'period', 'is_active', 'notification_type', 'offset_days', 'pointed_date'  ]
	list_display = ('efrom', 'ento', 'sent_to_user_filter', 'subject', 'period', 'is_active', 'on_time','execution_date', 'notification_type', 'pointed_date_filter' )
	actions = [export_as_csv_action("Exportar CSV", fields=list_display, header=True, force_fields=True),]
admin.site.register(EmailNotification, EmailNotificationAdmin)

#Use this by registrating of ModelAdmin in admin.site to specific cooper csv import
class CSVImportAdmin(ModelAdmin):
	''' Custom model to not have much editable!'''
	readonly_fields = ['file_name',
					   'upload_method',
					   'error_log_html',
					   'import_user']
	fields = [
				'model_name',
				'field_list',
				'upload_file',
				'file_name',
				'encoding',
				'upload_method',
				'error_log_html',
				'import_user']
	formfield_overrides = {
		models.CharField: {'widget': forms.Textarea(attrs={'rows':'4',
			   'cols':'60'})},
		}

	def save_model(self, request, obj, form, change):
		form.save()
		#TODO: Use a command  from App.management.commands.myCSVimporterLib import Command
		#      cmd = Command()
		if obj.upload_file:
			obj.file_name = obj.upload_file.name
			obj.encoding = ''
			defaults = self.filename_defaults(obj.file_name)
			members = open(settings.MEDIA_BASE + str(obj.upload_file))
			data = csv.DictReader(members)
			default_password = 'tsc_eclub'
			errors = [] 
			error = False
			coopnum = None
			for row in data:
				try:
					name = row['name'][0:29]
					lastname = row['lastname'][0:29]
					email = row['email']
					coop = row['coop']
					coopnum = row['coopnum']
					coopnum=coopnum.replace("COOP","")
					passw = row['password']
					vat = row['iva']
					vat = vat.replace("%","")
					tax = row['tax']
				except:
					errors.append("\n S'han de revisar les columnes")
					error = True
				
				if not error and not coopnum:
					errors.append("\n Falta num cooper")
				
				r_coop= Coop.objects.filter(name=coop)
				if not error and not r_coop:
					errors.append("\n Per %s no trobem la cooperativa %s" % (coopnum, coop))

				if not vat:
					vat = 0
				if not tax:
					tax = 0

				if coopnum and r_coop:
					user = None
					with transaction.atomic():
						try:
							try:
								user = User.objects.get(username = coopnum)
							except:
								print "not existing " + coopnum
								user = None
							
							if user:
								user.first_name = name
								user.last_name = lastname
								user.save()
							else:
								user = User.objects.create_user(coopnum, email, passw)
								user.is_staff = False
								user.first_name = name
								user.last_name = lastname
								user.save()

								if user:
									from django.contrib.auth.models import Group
									g = Group.objects.get(name='cooper') 
									g.user_set.add(user)
									
									cooper = cooper (user=user, coop=r_coop[0], coop_number=coopnum, assigned_vat=vat, advanced_tax=tax)
									cooper.save()
						except IntegrityError as e:
							errors.append("\n" + str(e))
							errors.append("\n" + str(row))
						except Exception as e:
							print e
							print lastname
							print name

			#errors = ["Finalitzat el procés"]
			if errors or error:
				obj.error_log = '\n'.join(errors)

			obj.import_user = str(request.user)
			obj.import_date = datetime.now()
			obj.save()

	def filename_defaults(self, filename):
		""" Override this method to supply filename based data """
		defaults = []
		splitters = {'/':-1, '.':0, '_':0}
		for splitter, index in splitters.items():
			if filename.find(splitter)>-1:
				filename = filename.split(splitter)[index]
		return defaults
admin.site.register(CSVImport, CSVImportAdmin)

'''
3.1) USER
'''
#Add any Invoice new Entity for COOPER below:
from Cooper.admin import user_admin_site

class tax_user(ModelAdmin):
	fields = ['value', 'min_base', 'max_base']
	list_display = ('value', 'min_base', 'max_base')
	actions = [export_as_csv_action("Exportar CSV", fields=list_display, header=True, force_fields=True),]
	def get_actions(self, request):
		actions = super(tax_user, self).get_actions(request)
		del actions['delete_selected']
		return actions

	def has_delete_permission(self, request):
		return False

	def has_add_permission(self, request):
		return False

	def __init__(self, *args, **kwargs):
		super(tax_user, self).__init__(*args, **kwargs)
		self.list_display_links = (None,)

	# to hide change and add buttons on main page:
	def get_model_perms(self, request): 
		return {'view': True}
user_admin_site.register(tax, tax_user)

class invoice_admin(ModelAdmin):
	list_filter = ('period',)
	model = invoice
	def status(self, obj):
		return obj.status()
	status.short_description = _(u"Estat")

	def queryset(self, request):
		if request.user.is_superuser:
			return self.model.objects.all()
		else:
			return self.model.objects.filter(cooper=bot_cooper(request.user).cooper(request))

	def get_form(self, request, obj=None, **kwargs):
		ModelForm = super(invoice_admin, self).get_form(request, obj, **kwargs)
		ModelForm.request = request 
		return ModelForm

	def get_changelist_form(self, request, **kwargs):
		current_form = self.form
		current_form.request = request

		current_period = bot_period(request.user).period( True, request )
		if current_period and not hasattr(self, 'period'):
			current_form.period = current_period
		
		if hasattr(self.model, 'status'):
			current_form.status = self.model.status
		else:
			current_form.status = None

		current_cooper = bot_cooper(request.user).cooper(request)
		if current_cooper and not hasattr(self.model, 'cooper'):
			current_form.cooper  = current_cooper 

		kwargs['form'] = current_form
		return super(invoice_admin, self).get_changelist_form(request, **kwargs)

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "client":
			if request.user.is_superuser:
				clients = client.objects.all()
			else:
				clients = bot_cooper(request.user).clients()
			kwargs["queryset"] = clients
		if db_field.name == "provider":
			if request.user.is_superuser:
				providers = provider.objects.all()
			else:
				providers = bot_cooper(request.user).providers()
			kwargs["queryset"] = providers
		return super(invoice_admin, self).formfield_for_foreignkey(db_field, request, **kwargs)
	class Media:
			js = (
				'invoice.js',   # app static folder
			)

from django.contrib import admin
class sales_line_inline(admin.TabularInline):
	model = sales_line
	fields = ['value', 'percent_invoiced_vat']
	list_display = ('value', 'percent_invoiced_vat', 'assigned_vat')
	def assigned_vat(self,obj):
		return obj.assigned_vat
	extra = 1

from Invoices.forms import sales_invoice_form
class sales_invoice_user (invoice_admin):
	form = sales_invoice_form
	model = sales_invoice
	change_list_template = 'admin/Invoices/salesInvoices/change_list.html'
	fields = ['client',] + ['period', 'num', 'date'] + ['who_manage',]
	list_display =  ('client',) + ('period', 'number', 'num', 'date', 'value') + ('invoiced_vat', 'assigned_vat', 'total', ) + ('who_manage', 'status', 'transfer_date')
	list_editable =  ('client',) + ('num', 'date') + ('who_manage',)
	list_export = ( 'clientName', 'clientCif') + ('period', 'number', 'num', 'date', 'value') + ('invoiced_vat', 'assigned_vat', 'total', ) + ('who_manage', 'status', 'transfer_date')
	inlines = [sales_line_inline]
	actions = [export_as_csv_action("Exportar CSV", fields=list_export, header=True, force_fields=True),]
	list_display_links = ( 'number', )
	def clientName(self, obj):
		return obj.client.name
	clientName.short_description = _(u"Client")

	def clientCif(self, obj):
		if obj.client.CIF:
			return obj.client.CIF
		else:
			return obj.client.otherCIF
	clientCif.short_description = _(u"Client (ID) ")

	def changelist_view(self, request, extra_context=None):
		response = super(sales_invoice_user, self).changelist_view(request, extra_context)
		try:
			qs_queryset = response.context_data["cl"].query_set
		except:
			qs_queryset = None
		if qs_queryset and extra_context is None:
			extra_context = {}
			from bots import bot_sales_invoice
			bot = bot_sales_invoice( qs_queryset )
			extra_context['sales_base'] = Decimal ( "%.2f" % bot.sales_base )
			extra_context['sales_invoiced_vat'] = Decimal ( "%.2f" % bot.sales_invoiced_vat )
			extra_context['sales_assigned_vat'] = Decimal ( "%.2f" % bot.sales_assigned_vat )
			extra_context['sales_total'] = Decimal ( "%.2f" % bot.sales_total )
		#Filter by period
		from Invoices.bots import bot_filters
		return bot_filters.filterbydefault(request, self, sales_invoice_user, extra_context)
user_admin_site.register(sales_invoice, sales_invoice_user)

class sales_invoice_admin(sales_invoice_user):
	fields = ['cooper', ] + sales_invoice_user.fields + ['status', 'transfer_date']
	list_display = ('cooper',) + sales_invoice_user.list_display  + ('status', 'transfer_date')
	list_display_links = ( 'number', )
	list_editable = ('cooper',) + sales_invoice_user.list_editable + ('transfer_date', )
	list_export = ('cooper',) + sales_invoice_user.list_export 
	list_filter = ('cooper','period', 'transfer_date')
	actions = sales_invoice_user.actions + [export_all_as_csv_action(_(u"Exportar tots CSV"), fields=list_export, header=True, force_fields=True),]
admin.site.register(sales_invoice, sales_invoice_admin)

class purchases_line_inline(admin.TabularInline):
	model = purchases_line
	fields = ['value', 'percent_vat', 'percent_irpf']
	extra = 1
from Invoices.forms import purchases_invoice_form
class purchases_invoice_user (invoice_admin):
	form = purchases_invoice_form
	model = purchases_invoice
	change_list_template = 'admin/Invoices/purchasesInvoices/change_list.html'
	fields = ['provider',] + ['period', 'num', 'date'] + ['who_manage', 'expiring_date']
	list_display =  ('provider',) + ('period', 'number', 'num', 'date', 'value') + ('vat', 'irpf', 'total') + ('who_manage', 'status', 'expiring_date', 'transfer_date')
	list_editable =  ('provider',) + ('num', 'date') + ('who_manage', 'expiring_date')
	list_export = ( 'providerName', 'providerCif') + ('period', 'number', 'num', 'date', 'value') + ('vat', 'irpf', 'total') + ('who_manage', 'status', 'expiring_date', 'transfer_date')
	inlines = [purchases_line_inline]
	actions = [export_as_csv_action("Exportar CSV", fields=list_export, header=True, force_fields=True),]
	list_display_links = ( 'number', )
	list_per_page = 1000
	def providerName(self, obj):
		return obj.provider.name
	providerName.short_description = _(u"provider")

	def providerCif(self, obj):
		if obj.provider.CIF:
			return obj.provider.CIF
		else:
			return obj.provider.otherCIF
	providerCif.short_description = _(u"provider (ID) ")

	def changelist_view(self, request, extra_context=None):
		#Get totals
		response = super(purchases_invoice_user, self).changelist_view(request, extra_context)
		try:
			qs_queryset = response.context_data["cl"].query_set
		except:
			qs_queryset = None
		if qs_queryset and extra_context is None:
			extra_context = {}
			from bots import bot_purchases_invoice
			bot = bot_purchases_invoice( qs_queryset )
			extra_context['purchases_base'] = Decimal ( "%.2f" % bot.purchases_base )
			extra_context['purchases_vat'] = Decimal ( "%.2f" % bot.purchases_vat )
			extra_context['purchases_irpf'] = Decimal ( "%.2f" % bot.purchases_irpf )
			extra_context['purchases_total'] = Decimal ( "%.2f" % bot.purchases_total )

		#Filter by period
		from Invoices.bots import bot_filters
		return bot_filters.filterbydefault(request, self, purchases_invoice_user, extra_context)
user_admin_site.register(purchases_invoice, purchases_invoice_user)

class purchases_invoice_admin (purchases_invoice_user):
	fields = ['cooper'] + purchases_invoice_user.fields + ['status', 'transfer_date']
	list_display = ('cooper',) + purchases_invoice_user.list_display
	list_editable = ('cooper',) + purchases_invoice_user.list_editable + ('transfer_date',)
	list_export = ('cooper',) + purchases_invoice_user.list_export
	list_filter = ('cooper','period',)
	actions = purchases_invoice_user.actions + [export_all_as_csv_action(_(u"Exportar tots CSV"), fields=list_export, header=True, force_fields=True),]
admin.site.register(purchases_invoice, purchases_invoice_admin)

class company_admin(ModelAdmin):
	fields = ['name', 'CIF', 'otherCIF']
	list_display = ('name', 'CIF', 'otherCIF')
	search_fields = ['name', 'CIF', 'otherCIF']
	actions = [export_as_csv_action("Exportar CSV", fields=list_display, header=True, force_fields=True),]

from Invoices.forms import client_form
class client_admin(company_admin):
	form = client_form
	model = client
class client_user(client_admin):
	def save_model(self, request, obj, form, change):
		obj.save()
		if not request.user.is_superuser:
			c = bot_cooper( request.user).cooper(request)
			if c:
				c.clients.add(obj)
	def get_model_perms(self, request): 
		return {'skip':True }
admin.site.register(client, client_admin)
user_admin_site.register(client, client_user)

from Invoices.forms import provider_form
from Invoices.models import provider
class provider_admin(company_admin):
	fields = company_admin.fields + ['iban', ]
	list_display = company_admin.list_display + ('iban', )
	search_fields = company_admin.search_fields + ['iban', ]
	model = provider

class provider_user(provider_admin):
	def save_model(self, request, obj, form, change):
		obj.save()
		if not request.user.is_superuser:
			c = bot_cooper( request.user).cooper(request)
			if c:
				c.providers.add(obj)
	def get_model_perms(self, request): 
		return {'skip':True }
admin.site.register(provider, provider_admin)
user_admin_site.register(provider, provider_user)

from Invoices.forms import period_payment_inline_form
class period_payment_inline(admin.TabularInline):
	model = period_payment
	form = period_payment_inline_form

from Invoices.forms import period_close_form

from Invoices.models import period_close_base_fields
class period_close_user(admin.ModelAdmin):
	form = period_close_form
	change_form_template = 'admin/Invoices/period_close/change_form.html'
	model = period_close
	inlines = [period_payment_inline]
	list_display = ('edit_link', 'print_link') + period_close_base_fields
	list_export = period_close_base_fields
	fieldsets = (
		(_(u'Període'), {'fields': ('period', 'cooper') }),
		(_('Emeses'), {'fields': (('sales_base', 'sales_invoiced_vat'), ('sales_total', 'sales_assigned_vat'))}),
		(_('Despeses'), {'fields': (('purchases_base', 'purchases_vat'), ('purchases_total', 'purchases_irpf'))}),
		(_('Seleccio IVA'), { 'fields': (('oficial_vat_total', 'assigned_vat_total'), 'vat_type') }),
		(_('Estalvi'), {'fields': ('savings_with_assigned_vat', 'savings_with_assigned_vat_donation')}),
		(_('Aportacio a la CIC'), {'fields': ('donation',)}),
		(_('Total impostos'), {'fields': (('total_vat', 'total_irpf'),)}),
		(_('Quota Trimestral'), {'fields': ('period_tax', 'advanced_tax' )}),
		(_('Totals'), {'fields': ('total', 'total_to_pay', 'total_balance', 'total_acumulated')}),
		(_('Tancar'), {'fields': ('closed',)}),
	)
	actions = [export_as_csv_action("Exportar CSV", fields=list_export, header=True, force_fields=True),]

	def savings_with_assigned_vat(self, obj):
		return obj.savings_with_assigned_vat()
	savings_with_assigned_vat.decimal = True
	savings_with_assigned_vat.short_description = _(u'IVA Facturat - Assignat (€)')

	def oficial_vat_total(self, obj):
		return obj.oficial_vat_total()
	oficial_vat_total.decimal = True
	oficial_vat_total.short_description = _(u'IVA Facturat - Despeses (€)')

	def assigned_vat_total(self, obj):
		return obj.assigned_vat_total()
	assigned_vat_total.decimal = True
	assigned_vat_total.short_description = _(u'IVA Assignat - Despeses (€)')

	def total_vat(self, obj):
		return obj.total_vat()

	def total_irpf(self, obj):
		return obj.total_irpf()

	def __init__(self, *args, **kwargs):
		super(period_close_user, self).__init__(*args, **kwargs)
		self.list_display_links = (None, )

	def queryset(self, request):
		return period_close.objects.filter(cooper=bot_cooper(request.user).cooper(request))

	def save_model(self, request, obj, form, change):

		#As we disable cooper and periods controls, we loaded their values in get_form so reload
		if obj.period is None:
			obj.period = form.period
			obj.cooper = form.cooper
		obj.save()

		if obj.closed and obj.advanced_tax > 0:
			c = cooper.objects.get(pk=obj.cooper.id)
			c.advanced_tax = 0
			c.save()

		form.save_m2m()

		if obj.closed:
			from Invoices.bots import bot_period_payment
			bot_period_payment(obj).create_sales_movements_for_period()

	def edit_link(self, obj):
		if obj is None:
			can_edit = False
		else:
			can_edit =self.exists_opened_period( obj.cooper.user ) and self.exists_closed_period( obj.cooper.user ) and not self.exists_closed_period_done ( obj )
		if can_edit:
			return u'<a href="/cooper/%s/%s/%s">%s</a>' % (
				 obj._meta.app_label, obj._meta.module_name, obj.id, obj.period)
		else:
			return obj.period
	edit_link.allow_tags = True
	edit_link.short_description = _(u"Període")

	def print_link(self, obj):
		
		if obj is None:
			can_print = False
		else:
			can_print = self.exists_closed_period_done ( obj )
		if can_print:
			return u'<a href="/invoices/print/%s">%s</a>' % ( obj.id, obj.period)
		else:
			return (u"-")
	print_link.allow_tags = True
	print_link.short_description = _(u"PDF")

	def exists_opened_period(self, user):
		return bot_period(user).period(False) is not None

	def exists_closed_period(self, user):
		current_period = bot_period(user).period(False)
		current_cooper = bot_cooper(user).cooper(False)
		if current_period is not None:
			return period_close.objects.filter(period=current_period, cooper=current_cooper).count()>0
		return False

	def exists_closed_period_done(self, pc):
		return period_close.objects.get(pk=pc.id).closed

	def has_add_permission(self, request):
		if request.user.is_superuser:
			 return True
		return self.exists_opened_period( request.user ) and not self.exists_closed_period( request.user )

	def has_change_permission(self, request, obj=None):
		if request.user.is_superuser:
			return True
		if obj is None:
			return True
		else:
			return self.exists_opened_period( obj.cooper.user ) and self.exists_closed_period( obj.cooper.user ) and not self.exists_closed_period_done ( obj )

	def get_actions(self, request):
		actions = super(period_close_user, self).get_actions(request)
		del actions['delete_selected']
		return actions

	# to hide change and add buttons on main page:
	def get_model_perms(self, request): 
		return {'historial':True, 
			'canAdd': self.exists_opened_period( request.user ) and not self.exists_closed_period( request.user ),
			'canEdit': self.exists_opened_period( request.user ) }

	def get_form(self, request, obj=None, **kwargs):
		ModelForm = super(period_close_user, self).get_form(request, obj, **kwargs)
		ModelForm.is_new = obj is None
		ModelForm.request = request
		if obj:
			ModelForm.obj = obj
		ModelForm.current_fields = self.list_export
		if obj is not None:
			ModelForm.period = obj.period
			ModelForm.cooper = obj.cooper
			bot_period_close( obj.period, obj.cooper, obj).set_period_close_form_readonly(ModelForm)
		return ModelForm



	class Media:
			js = (
				'period_close.js',   # app static folder
			)
user_admin_site.register(period_close, period_close_user)

class period_close_admin (period_close_user):
	change_list_template = 'admin/Invoices/period_close/change_list_admin.html'
	list_display = ('cooper', ) + period_close_user.list_display
	list_export = ('cooper',) + period_close_user.list_export
	list_per_page = 1000
	actions = period_close_user.actions + [export_all_as_csv_action(_(u"Exportar tots CSV"), fields=list_export, header=True, force_fields=True),]
	def edit_link(self, obj):
		if obj is None:
			can_edit = False
		else:
			can_edit = True
		if can_edit:
			return u'<a href="/admin/%s/%s/%s">%s</a>' % (
				 obj._meta.app_label, obj._meta.module_name, obj.id, obj.period)
		else:
			return obj.period
	edit_link.allow_tags = True
	edit_link.short_description = _(u"Període")
	search_fields = ['coop_number', 'user__username', 'user__first_name']
	list_filter = ('period',  First_Period_Filter, Closing_Filter )
	def queryset(self, request):
		return period_close.objects.all()
	def changelist_view(self, request, extra_context=None):
		#Get totals
		response = super(period_close_user, self).changelist_view(request, extra_context)
		try:
			qs_queryset = response.context_data["cl"].query_set
		except:
			qs_queryset = None

		if qs_queryset and extra_context is None:
			totals = {}
			numeric_fields = ('sales_base', 'sales_invoiced_vat', 'sales_assigned_vat', 'sales_total', 
							'purchases_base', 'purchases_vat', 'purchases_irpf', 'purchases_total',
							'oficial_vat_total', 'assigned_vat_total', 'savings_with_assigned_vat', 'savings_with_assigned_vat_donation',
							'total_vat', 'total_irpf','period_tax', 'advanced_tax','donation', 'total', 'total_to_pay')
			#init
			for field in numeric_fields:
					totals[field] = Decimal ( "0.00" )

			for period_closed in qs_queryset:
				#load values
				for field in numeric_fields:
					try:
						#print command will rise exception, so don't remove!!!
						print Decimal ( "%.2f" % bot_object( field, period_closed ).value() )
						totals[field] = Decimal ( "%.2f" % bot_object( field, period_closed ).value() )
					except:
						totals[field] = bot_object( field, period_closed ).value()()

			#send to template
			extra_context = {}
			for field in numeric_fields:
				extra_context[field] = totals[field]

		#Filter by period
		from Invoices.bots import bot_filters
		return bot_filters.filterbydefault(request, self, period_close_user, extra_context)
admin.site.register(period_close, period_close_admin)

class balance_line_inline(admin.TabularInline):
	model = invoice
	fields = ['status', 'date', 'transfer_date']
	extra = 0
	def status(self, obj):
		return obj.status()
	def total(self, obj):
		return obj.total()
	def get_queryset(self, request):
		current_period = bot_period(request.user).period()
		if current_period:
			return self.model.objects.filter(
					who_manage=manage_CHOICE_COOP).exclude(
					date__lte=current_period.first_day,
					transfer_date__isnull=True)
		else:
			return self.model.objects.filter(who_manage=manage_CHOICE_COOP)
	def has_delete_permission(self, request, obj=None):
		return request.user.is_superuser
	def has_add_permission(self, request, obj=None):
		return False

from Invoices.forms import invoice_form_balance 
class sales_invoice_inline_balance(balance_line_inline):
	model = sales_invoice
	form = invoice_form_balance
	fields = ['client', 'total'] + balance_line_inline.fields
	def get_readonly_fields(self, request, obj=None):
		if request.user.is_superuser:
			return ()
		else:
			return balance_line_inline.readonly_fields + ( 'client',) + ( 'date',  'total', 'transfer_date', )
class purchases_invoice_inline_balance(balance_line_inline):
	model = purchases_invoice
	form = invoice_form_balance
	fields = ['provider', 'total', 'status', 'expiring_date', 'transfer_date']
	def get_readonly_fields(self, request, obj=None):
		if request.user.is_superuser:
			return ()
		else:
			#if self.instance.transfer_date is not None:
			#	rfields = balance_line_inline.readonly_fields + ( 'expiring_date', )
			return ( 'provider', ) + ( 'date',  'total', 'transfer_date', )

from Invoices.forms import movement_form_balance
class sales_movement_inline(admin.TabularInline):
	form = movement_form_balance
	model = sales_movement
	fields = ['value', 'concept', 'planned_date', 'execution_date', 'status', 'currency']
	list_filter = ('status', 'currency')
	extra = 0
	def has_delete_permission(self, request, obj=None):
		return request.user.is_superuser
	def get_readonly_fields(self, request, obj=None):
		if request.user.is_superuser:
			return self.readonly_fields
		else:
			#if self.instance.transfer_date is not None:
			#	rfields = balance_line_inline.readonly_fields + ( 'expiring_date', )
			return ( 'execution_date', )
class purchases_movement_inline(admin.TabularInline):
	model = purchases_movement
	form = movement_form_balance
	fields = [ 'value', 'concept', 'petition_date', 'acceptation_date', 'execution_date', 'status', 'currency']
	extra = 0
	def has_delete_permission(self, request, obj=None):
		return request.user.is_superuser
	def get_readonly_fields(self, request, obj=None):
		if request.user.is_superuser:
			return self.readonly_fields
		else:
			#if self.instance.transfer_date is not None:
			#	rfields = balance_line_inline.readonly_fields + ( 'expiring_date', )
			return ( 'acceptation_date', 'execution_date', )

class period_admin(ModelAdmin):
	fields = ['label', 'first_day', 'date_open', 'date_close']
	list_display = ('label', 'first_day', 'date_open', 'date_close')
	actions = [export_as_csv_action("Exportar CSV", fields=list_display, header=True, force_fields=True),]
admin.site.register(period, period_admin)

from Invoices.forms import cooper_admin_form
class cooper_admin(ModelAdmin):
	form = cooper_admin_form
	model = 'cooper'
	list_per_page = 600
	fields = ['user', 'coop_number', 'assigned_vat', 'coop', 'extra_days', 'advanced_tax']
	list_display = ('user','coopnumber', 'email', 'assigned_vat', 'coop', 'extra_days', 'advanced_tax', 'date_joined')
	list_display_links = ('user','coopnumber')
	search_fields = ['coop_number', 'user__username', 'user__first_name']
	list_filter = ('coop',  First_Period_Filter, Closing_Filter )
	actions = [export_as_csv_action("Exportar CSV", fields=list_display, header=True, force_fields=True),] 

	def date_joined(self,obj):
		return obj.user.date_joined
	date_joined.short_description = _(u"Data d'alta")
	date_joined.admin_order_field = 'user__date_joined'
	def firstname(self,obj):
		return obj.user.first_name
	firstname.admin_order_field = 'user__first_name'
	firstname.short_description = _(u"Nom")
	def lastname(self,obj):
		return obj.user.last_name
	lastname.admin_order_field = 'user__last_name'
	lastname.short_description = _(u"Cognom")
	def coopnumber(self,obj):
		return "%04d" % obj.coop_number
	coopnumber.short_description = _(u"nº COOP")
	coopnumber.admin_order_field = 'coop_number'
	def first_period(self, obj):
		qs = period.objects.filter(date_close__gt = (obj.user.date_joined  ) , first_day__lte = obj.user.date_joined  + timedelta(days=9) )
		if qs.count() > 0:
			return qs[0]
		return None
	first_period.short_description = _(u"Període inicial")
admin.site.register(cooper, cooper_admin)

from Invoices.forms import cooper_admin_form

class cooper_user_balance(ModelAdmin):
	model = cooper_proxy_balance
	list_per_page = 600
	fields = ['coop_number']
	readonly_fields = ['coop_number']
	list_display = ('coop_number', 'balance', 'balance_euro', 'balance_eco', 'balance_btc')
	list_display_links = ('coop_number', )
	actions = [export_as_csv_action("Exportar CSV", fields=list_display, header=True, force_fields=True),]
	inlines = [sales_invoice_inline_balance, purchases_invoice_inline_balance, sales_movement_inline, purchases_movement_inline]
	def has_add_permission(self, request, obj=None):
		return False
	def get_actions(self, request):
		actions = super(cooper_user_balance, self).get_actions(request)
		del actions['delete_selected']
		return actions

	def has_delete_permission(self, request, obj=None):
		return False

	def balance_euro(self, obj):
		current_period = bot_period(obj.user).period()
		bot = bot_balance(current_period, obj)
		return bot.total_previous(currencies.objects.get(name="EURO")) + bot.total(currencies.objects.get(name="EURO"))
	balance_euro.short_description = _(u"Balanç EURO")

	def balance_btc(self, obj):
		current_period = bot_period(obj.user).period()
		bot = bot_balance(current_period, obj)
		return bot.total_previous(currencies.objects.get(name="BTC")) + bot.total(currencies.objects.get(name="BTC"))
	balance_btc.short_description = _(u"Balanç BTC")

	def balance_eco(self, obj):
		current_period = bot_period(obj.user).period()
		bot = bot_balance(current_period, obj)
		return bot.total_previous(currencies.objects.get(name="ECO")) + bot.total(currencies.objects.get(name="ECO"))
	balance_eco.short_description = _(u"Balanç ECOS")
	def balance(self, obj):
		current_period = bot_period(obj.user).period()
		bot = bot_balance(current_period, obj)
		return bot.total_previous() + bot.total()
	balance.short_description = _(u"Balanç saldo")

	def get_form(self, request, obj=None, **kwargs):
		ModelForm = super(cooper_user_balance, self).get_form(request, obj, **kwargs)
		ModelForm.request = request 
		ModelForm.balance_euro = Decimal ( "%.2f" % self.balance_euro( obj ) )
		ModelForm.balance_btc = Decimal ( "%.2f" % self.balance_btc( obj ) )
		ModelForm.balance_eco = Decimal ( "%.2f" % self.balance_eco( obj ) )
		ModelForm.balance = Decimal ( "%.2f" % self.balance( obj ) )
		return ModelForm

	def get_model_perms(self, request): 
		if request.user.is_superuser:
			return {'historial':True, 
				'canAdd': False,
				'canEdit': True }
		else:
			cooper = bot_cooper( request.user ).cooper( request )
			perms = {}
			if cooper:
				perms = {'direct_to_change_form':True, 
						'change_form_url': cooper.id }
			return perms
user_admin_site.register(cooper_proxy_balance, cooper_user_balance)

class cooper_admin_transaction( cooper_user_balance):
	model = 'cooper_proxy_transactions'
admin.site.register(cooper_proxy_transactions, cooper_admin_transaction)


from Invoices.models import movement_STATUSES
class movements_admin(ModelAdmin):
	form = movement_form_balance
	list_filter = ('cooper', 'currency',)
	list_editable = ('execution_date', 'currency')
	def status(self, obj):
		return movement_STATUSES[obj.status()][1]
	status.short_description = (u"Estat")

class sales_movements_admin(movements_admin):
	model = sales_movement
	fields = ['cooper', 'value', 'concept', 'planned_date', 'execution_date', 'status', 'currency']
	list_display = ('cooper', 'value', 'concept', 'planned_date', 'execution_date', 'status', 'currency')
admin.site.register(sales_movement, sales_movements_admin)

class purchases_movements_admin(movements_admin):
	model = purchases_movement
	fields = ['cooper', 'value', 'concept', 'petition_date', 'execution_date', 'status', 'currency']
	list_display = ('cooper', 'value', 'concept', 'petition_date', 'execution_date', 'status', 'currency')

admin.site.register(purchases_movement, purchases_movements_admin)

class cooper_companies_user(ModelAdmin):
	model = 'cooper_proxy_companies'
	fields = ['clients', 'providers']
	filter_horizontal = ('clients', 'providers')
	list_display = ('coop_number', 'cooper_clients', 'cooper_providers')
	list_display_links = ('coop_number',)

	def queryset(self, request):
		return cooper.objects.filter(user=request.user)
	def cooper_clients(self, obj):
		return "\n".join([ p.__unicode__() + "<br>" for p in obj.clients.all()])
	cooper_clients.allow_tags = True
	cooper_clients.short_description = _(u"Els meus clients")
	def cooper_providers(self, obj):
		return "\n".join([ p.__unicode__() + "<br>" for p in obj.providers.all()])
	cooper_providers.allow_tags = True
	cooper_providers.short_description = _(u"Els meus proveïdors")
	def get_model_perms(self, request): 
		cooper = bot_cooper( request.user ).cooper( request )
		perms = {}
		if cooper:
			perms = {'direct_to_change_form':True, 
			'change_form_url': bot_cooper( request.user ).cooper().id }
		return perms
user_admin_site.register(cooper_proxy_companies, cooper_companies_user)

class cooper_companies_admin(cooper_companies_user):
	model = 'cooper_proxy_companies'
	fields = ['clients', 'providers']
	filter_horizontal = ('clients', 'providers')
	list_display = ('coop_number', 'cooper_clients', 'cooper_providers')
	list_display_links = ('coop_number',)

	def queryset(self, request):
		return cooper.objects.filter(user=request.user)
	def cooper_clients(self, obj):
		return "\n".join([ p.__unicode__() + "<br>" for p in obj.clients.all()])
	cooper_clients.allow_tags = True
	cooper_clients.short_description = _(u"Els meus clients")
	def cooper_providers(self, obj):
		return "\n".join([ p.__unicode__() + "<br>" for p in obj.providers.all()])
	cooper_providers.allow_tags = True
	cooper_providers.short_description = _(u"Els meus proveïdors")
	def get_model_perms(self, request): 
		return {'direct_to_change_form':False }
