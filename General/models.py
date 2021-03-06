#encoding=utf-8
from django.utils.safestring import mark_safe
from django.db import models

from mptt.models import MPTTModel
from mptt.fields import TreeForeignKey, TreeManyToManyField
from datetime import date, timedelta
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import gettext_lazy as __
from decimal import Decimal

from itertools import chain

# Create your models here.

a_strG = "<a onclick='return showRelatedObjectLookupPopup(this);' href='/admin/General/"
a_strW = "<a onclick='return showRelatedObjectLookupPopup(this);' href='/admin/Welcome/"
#a_str2 = "?_popup=1&_changelist_filters=_popup=1&t=human' target='_blank' style='margin-left:-100px'>"
a_str2 = "?_popup=1&t=human' target='_blank' >"
a_str3 = "?_popup=1&t=human' target='_blank'>"

a_edit = '<b>Editar</b>'

ul_tag1 = '<ul style="margin-left:-10em;">'
ul_tag = '<ul>'

str_none = __('(cap)')
str_remove = 'treu'

def erase_id_link(field, id):
	out = '<a class="erase_id_on_box" name="'+str(field)+','+str(id)+'" href="javascript:;">'+str_remove+'</a>'
	return out

#	 C O N C E P T S - (Conceptes...)

class Concept(MPTTModel):	# Abstract
	name = models.CharField(unique=True, verbose_name=_(u"Nom"), max_length=200, help_text=_(u"El nom del Concepte"), default="")
	description = models.TextField(blank=True, verbose_name=_(u"Descripció"))
	parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

	def __unicode__(self):
		return self.name

	class Meta:
		abstract = True
		verbose_name = _(u"Concepte")
		verbose_name_plural = _(u"c- Conceptes")


class Type(Concept):	# Create own ID's (TREE)
	#concept = models.OneToOneField('Concept', primary_key=True, parent_link=True)
	clas = models.CharField(blank=True, verbose_name=_(u"Clase"), max_length=200,
													help_text=_(u"Model de django o classe python associada al Tipus"))
	class Meta:
		verbose_name = _(u"c- Tipus")

	def __unicode__(self):
		if self.clas is None or self.clas == '':
			return self.name
		else:
			return self.name+' ('+self.clas+')'



#	 B E I N G S - (Éssers, Entitats, Projectes...)

class Being(models.Model):	# Abstract
	name = models.CharField(verbose_name=_(u"Nom"), blank=False, null=False, max_length=200, help_text=_(u"El nom de la Entitat"))
	#being_type = TreeForeignKey('Being_Type', blank=True, null=True, verbose_name=_(u"Tipus d'entitat"))
	birth_date = models.DateField(blank=True, null=True, verbose_name=_(u"Data de naixement"), help_text=_(u"El dia que va començar a existir"))
	death_date = models.DateField(blank=True, null=True, verbose_name=_(u"Data d'acabament"), help_text=_(u"El dia que va deixar d'existir"))

	class Meta:
		abstract = True

	def __unicode__(self):
		return self.name.encode("utf-8")

class Being_Type(Type):
	typ = models.OneToOneField('Type', primary_key=True, parent_link=True)
	class Meta:
		verbose_name= _(u"Tipus d'entitat")
		verbose_name_plural = _(u"e--> Tipus d'entitats")


class Human(Being):	# Create own ID's
	nickname = models.CharField(max_length=50, blank=True, verbose_name=_(u"Sobrenom"), help_text=_(u"El sobrenom (nickname) de l'entitat Humana"))
	email = models.EmailField(max_length=100, blank=False, null=False, verbose_name=_(u"Email"), help_text=_(u"L'adreça d'email principal de l'entitat humana"))
	telephone_cell = models.CharField(max_length=20, blank=True, null=True, verbose_name=_(u"Telèfon mòbil"), help_text=_(u"El telèfon principal de l'entitat Humana"))
	telephone_land = models.CharField(max_length=20, blank=True, verbose_name=_(u"Telèfon fix"))
	website = models.CharField(max_length=100, blank=True, verbose_name=_(u"Web"), help_text=_(u"L'adreça web principal de l'entitat humana"))
	description = models.TextField(blank=True, null=True, verbose_name=_(u"Descripció entitat"))

	jobs = TreeManyToManyField('Job', through='rel_Human_Jobs', verbose_name=_(u"Activitats, Oficis"), blank=True, null=True)
	addresses = models.ManyToManyField('Address', through='rel_Human_Addresses', verbose_name=_(u"Adreçes"), blank=True, null=True)
	regions = models.ManyToManyField('Region', through='rel_Human_Regions', verbose_name=_(u"Regions"), blank=True, null=True)
	records = models.ManyToManyField('Record', through='rel_Human_Records', verbose_name=_(u"Registres"), blank=True, null=True)
	materials = models.ManyToManyField('Material', through='rel_Human_Materials', verbose_name=_(u"obres Materials"), blank=True, null=True)
	nonmaterials = models.ManyToManyField('Nonmaterial', through='rel_Human_Nonmaterials', verbose_name=_(u"obres Inmaterials"), blank=True, null=True)
	persons = models.ManyToManyField('Person', through='rel_Human_Persons', related_name='hum_persons', verbose_name=_(u"Persones"), blank=True, null=True)
	projects = models.ManyToManyField('Project', through='rel_Human_Projects', related_name='hum_projects', verbose_name=_(u"Projectes"), blank=True, null=True)
	companies = models.ManyToManyField('Company', through='rel_Human_Companies', related_name='hum_companies', verbose_name=_(u"Empreses"), blank=True, null=True)

	class Meta:
		verbose_name = _(u"Humà")
		verbose_name_plural = _(u"e- Humans")

	def __unicode__(self):
		if self.nickname is None or self.nickname == '':
			return self.name
		else:
			return self.nickname+' ('+self.name+')'

	def _my_accounts(self):
		return list(chain(self.accountsCes.all(), self.accountsCrypto.all(), self.accountsBank.all()))
	#_my_accounts.list = []
	accounts = property(_my_accounts)

	def _selflink(self, a_edit="<b>Editar</b>", admin_path="/admin/"):
		a_strG = "<a onclick='return showRelatedObjectLookupPopup(this);' href='" + admin_path + "General/"
		if self.id:
			if hasattr(self, 'person'):
				return mark_safe( a_strG + "person/" + str(self.person.id) + a_str2 + a_edit + "</a>") # % str(self.id))
			elif hasattr(self, 'project'):
				return mark_safe( a_strG + "project/" + str(self.project.id) + a_str2 + a_edit + "</a>")# % str(self.id) )
		else:
			return "Not present"
	_selflink.allow_tags = True
	_selflink.short_description = ''
	self_link = property (_selflink)
	def self_link_no_pop(self, next, admin="/admin/", edit_caption = "Editar"):
		if self.id:
			if hasattr(self, 'person'):
				id = self.person.id
				slug = "person"
			elif hasattr(self, 'project'):
				id = self.project.id
				slug = "project"
			return mark_safe( "<a href='%sGeneral/%s/%s%s'>%s</a>") % ( admin, slug, str(id), next,  edit_caption)
		else:
			return "Not present"
	self_link_no_pop.allow_tags = True
	self_link_no_pop.short_description = ''

	def _ic_membership(self):
		try:
			#print self.ic_membership_set.all()
			if hasattr(self, 'ic_person_membership_set'):
				ic_ms = self.ic_person_membership_set.all()
				out = ul_tag
				for ms in ic_ms:
					out += '<li>'+a_strW + "ic_person_membership/" + str(ms.id) + a_str3 + '<b>'+ms.name +"</b></a></li>"
				return out+'</ul>'
			elif hasattr(self, 'ic_project_membership_set'):
				ic_ms = self.ic_project_membership_set.all()
				out = ul_tag
				for ms in ic_ms:
					out += '<li>'+a_strW + "ic_project_membership/" + str(ms.id) + a_str3 + '<b>'+ms.name +"</b></a></li>"
				if out == ul_tag:
					return str_none
				return out+'</ul>'
			return str_none
		except:
			return str_none
	_ic_membership.allow_tags = True
	_ic_membership.short_description = _(u"reg.Altes Soci")

	def _fees_to_pay(self):
		try:
			if self.out_fees.all().count() > 0:
				out = ul_tag
				for fe in self.out_fees.all():
					if not fe.payed:
						out += '<li>'+a_strW + "fee/" + str(fe.id) + a_str3 +'<b>'+ fe.name + "</b></a></li>"
				if out == ul_tag:
					return str_none
				return out+'</ul>'
			return str_none
		except:
			return str_none
	_fees_to_pay.allow_tags = True
	_fees_to_pay.short_description = _(u"Quotes per pagar")

	def __init__(self, *args, **kwargs):
		super(Human, self).__init__(*args, **kwargs)

		if not 'rel_tit' in globals():
			rel_tit = Relation.objects.get(clas='holder')

		#print 'I N I T	 H U M A N :	'+self.name

		if hasattr(self, 'accountsCes') and self.accountsCes.count() > 0:
			recrels = rel_Human_Records.objects.filter(human=self, record__in=self.accountsCes.all())
			if recrels.count() == 0:
				for acc in self.accountsCes.all():
					newrec, created = rel_Human_Records.objects.get_or_create(human=self, record=acc, relation=rel_tit)
					#print '- new_REC acc_Ces: CREATED:'+str(created)+' :: '+str(newrec)

		if hasattr(self, 'accountsBank') and self.accountsBank.count() > 0:
			recrels = rel_Human_Records.objects.filter(human=self, record__in=self.accountsBank.all())
			if recrels.count() == 0:
				for acc in self.accountsBank.all():
					newrec, created = rel_Human_Records.objects.get_or_create(human=self, record=acc, relation=rel_tit)
					#print '- new_REC acc_Bank: CREATED:'+str(created)+' :: '+str(newrec)

		if hasattr(self, 'accountsCrypto') and self.accountsCrypto.count() > 0:
			recrels = rel_Human_Records.objects.filter(human=self, record__in=self.accountsCrypto.all())
			if recrels.count() == 0:
				for acc in self.accountsCrypto.all():
					newrec, created = rel_Human_Records.objects.get_or_create(human=self, record=acc, relation=rel_tit)
					#print '- new_REC acc_Crypto: CREATED:'+str(created)+' :: '+str(newrec)

			#print 'recrels: '+str(recrels)
			#print self.accountsCes.all()
			#print self.records.all()
			#if hasattr(self.records)
			#self.project = Project.objects.get(nickname='CIC')


class Person(Human):
	human = models.OneToOneField('Human', primary_key=True, parent_link=True)
	surnames = models.CharField(max_length=200, blank=False, null=False, verbose_name=_(u"Cognoms"), help_text=_(u"Els cognoms de la Persona"))
	id_card = models.CharField(max_length=9, blank=False, null=False, verbose_name=_(u"DNI/NIE"))
	email2 = models.EmailField(blank=True, verbose_name=_(u"Email alternatiu"))
	nickname2 = models.CharField(max_length=50, blank=True, verbose_name=_(u"Sobrenom a la Xarxa Social"))

	class Meta:
		verbose_name= _(u'Persona')
		verbose_name_plural= _(u'e- Persones')

	def __unicode__(self):
		if self.nickname is None or self.nickname == '':
			if self.surnames is None or self.surnames == '':
				return self.name+' '+self.nickname2
			else:
				return self.name+' '+self.surnames
		else:
			#return self.nickname
			if self.surnames is None or self.surnames == '':
				return self.name+' ('+self.nickname+')'
			else:
				return self.name+' '+self.surnames+' ('+self.nickname+')'


class Project(MPTTModel, Human):
	human = models.OneToOneField('Human', primary_key=True, parent_link=True)
	project_type = TreeForeignKey('Project_Type', blank=True, null=True, verbose_name=_(u"Tipus de projecte"))
	parent = TreeForeignKey('self', null=True, blank=True, related_name='subprojects', verbose_name=_(u"Projecte Marc"))
	socialweb = models.CharField(max_length=100, blank=True, verbose_name=_(u"Web Social"))
	email2 = models.EmailField(blank=True, verbose_name=_(u"Email alternatiu"))

	ecommerce = models.BooleanField(default=False, verbose_name=_(u"Comerç electrònic?"))
	#images = models.ManyToManyField('Image', blank=True, null=True, verbose_name=_(u"Imatges"))

	def _is_collective(self):
		if self.persons.count() < 2 and self.projects.count() < 2:
			return False
		else:
			return True
	_is_collective.boolean = True
	_is_collective.short_description = _(u"és col·lectiu?")
	collective = property(_is_collective)

	#ref_persons = models.ManyToManyField('Person', blank=True, null=True, verbose_name=_(u"Persones de referència"))

	class Meta:
		verbose_name= _(u'Projecte')
		verbose_name_plural= _(u'e- Projectes')

	def _get_ref_persons(self):
		return self.human_persons.filter(relation__clas='reference')

	def _ref_persons(self):
		prs = self._get_ref_persons()
		if prs.count() > 0:
			out = ul_tag
			for pr in prs:
				out += '<li>'+str(pr)+'</li>'
			return out+'</ul>'
		return str_none
	_ref_persons.allow_tags = True
	_ref_persons.short_description = _(u"Pers.de Referència?")

	def __unicode__(self):
		if self.nickname is None or self.nickname == '':
			if self.project_type:
				return self.name+' ('+self.project_type.name+')'
			else:
				return self.name
		else:
			return self.nickname+' ('+self.name+')'


class Project_Type(Being_Type):
	being_type = models.OneToOneField('Being_Type', primary_key=True, parent_link=True)
	class Meta:
		verbose_name = _(u"Tipus de Projecte")
		verbose_name_plural = _(u"e-> Tipus de Projectes")



class Company(Human):
	human = models.OneToOneField('Human', primary_key=True, parent_link=True)
	company_type = TreeForeignKey('Company_Type', null=True, blank=True, verbose_name=_(u"Tipus d'empresa"))
	legal_name = models.CharField(max_length=200, blank=True, null=True, verbose_name=_(u"Nom Fiscal"))
	id_card_es = models.CharField(verbose_name=_(u"CIF / NIF / NIE"), blank=True, null=True, help_text=_(u"NIF:12345678A - CIF: A12345678 - NIE: X12345678A del proveïdor a qui es factura."), max_length=200)
	id_card_non_es = models.CharField(verbose_name=_(u"Altres identificadors"), null=True, blank=True, help_text=_(u"Camps no CIF / NIF / NIE del proveïdor a qui es factura."), max_length=50)
	class Meta:
		verbose_name = _(u"Empresa")
		verbose_name_plural = _(u"e- Empreses")
	def vat_number(self):
		return self.id_card_es if self.id_card_es else (self.card_non_es if self.card_non_es else "<missing vat number>")

class Company_Type(Being_Type):
	being_type = models.OneToOneField('Being_Type', primary_key=True, parent_link=True)
	class Meta:
		verbose_name = _(u"Tipus d'Empresa")
		verbose_name_plural = _(u"e-> Tipus d'Empreses")



class rel_Human_Jobs(models.Model):
	human = models.ForeignKey('Human')
	job = TreeForeignKey('Job', verbose_name=_(u"Ofici"))
	relation = TreeForeignKey('Relation', related_name='hu_job+', blank=True, null=True, verbose_name=_(u"relació"))
	class Meta:
		verbose_name = _(u"H_ofi")
		verbose_name_plural = _(u"Oficis de l'entitat")
	def __unicode__(self):
		if self.relation:
			if self.relation.gerund is None or self.relation.gerund == '':
				return self.job.__unicode__()
			else:
				return self.relation.gerund+' > '+self.job.__unicode__()
		else:
			return self.job.__unicode__()

class rel_Human_Addresses(models.Model):
	human = models.ForeignKey('Human')
	address = models.ForeignKey('Address', related_name='rel_human', verbose_name=_(u"Adreça"),
		 help_text=_(u"Un cop escollida l'adreça, desa el perfil per veure el seu nom aquí."))
	relation = TreeForeignKey('Relation', related_name='hu_adr+', blank=True, null=True, verbose_name=_(u"relació"))
	main_address = models.BooleanField(default=False, verbose_name=_(u"Adreça principal?"))
	class Meta:
		verbose_name = _(u"H_adr")
		verbose_name_plural = _(u"Adreçes de l'entitat")
	def __unicode__(self):
		if self.relation is None or self.relation.gerund is None or self.relation.gerund == '':
			return self.address.__unicode__()
		else:
			return self.relation.gerund+' > '+self.address.__unicode__()
	def _is_main(self):
		return self.main_address
	_is_main.boolean = True
	is_main = property(_is_main)
	def _selflink(self):
		if self.address:
			return self.address._selflink()
	_selflink.allow_tags = True
	_selflink.short_description = ''

class rel_Human_Regions(models.Model):
	human = models.ForeignKey('Human')
	region = TreeForeignKey('Region', verbose_name=_(u"Regió"))
	relation = TreeForeignKey('Relation', related_name='hu_reg+', blank=True, null=True, verbose_name=_(u"relació"))
	class Meta:
		verbose_name = _(u"H_reg")
		verbose_name_plural = _(u"Regions vinculades")
	def __unicode__(self):
		if self.relation.gerund is None or self.relation.gerund == '':
			return self.region.__unicode__()
		else:
			return self.relation.gerund+' > '+self.region.__unicode__()


class rel_Human_Records(models.Model):
	human = models.ForeignKey('Human')
	record = models.ForeignKey('Record', verbose_name=_(u"Registre"))
	relation = TreeForeignKey('Relation', related_name='hu_rec+', blank=True, null=True, verbose_name=_(u"relació"))
	class Meta:
		verbose_name = _(u"H_rec")
		verbose_name_plural = _(u"Registres vinculats")
	def __unicode__(self):
		if not hasattr(self.relation, 'gerund') or self.relation.gerund is None or self.relation.gerund == '':
			return self.record.__unicode__()
		else:
			if not hasattr(self.record, 'record_type') or self.record.record_type is None or self.record.record_type == '':
				return self.relation.gerund+' > '+self.record.__unicode__()
			return self.record.record_type.name+': '+self.relation.gerund+' > '+self.record.__unicode__()
	def _selflink(self):
		return self.record._selflink()
	_selflink.allow_tags = True
	_selflink.short_description = ''

class rel_Human_Materials(models.Model):
	human = models.ForeignKey('Human')
	material = models.ForeignKey('Material', verbose_name=_(u"obra Material"))
	relation = TreeForeignKey('Relation', related_name='hu_mat+', blank=True, null=True, verbose_name=_(u"relació"))
	class Meta:
		verbose_name = _(u"H_mat")
		verbose_name_plural = _(u"Obres materials")
	def __unicode__(self):
		if not hasattr(self.relation, 'gerund') or self.relation.gerund is None or self.relation.gerund == '':
			return self.material.__unicode__()
		else:
			return self.relation.gerund+' > '+self.material.__unicode__()

class rel_Human_Nonmaterials(models.Model):
	human = models.ForeignKey('Human')
	nonmaterial = models.ForeignKey('Nonmaterial', verbose_name=_(u"obra Inmaterial"))
	relation = TreeForeignKey('Relation', related_name='hu_non+', blank=True, null=True, verbose_name=_(u"relació"))
	class Meta:
		verbose_name = _(u"H_inm")
		verbose_name_plural = _(u"Obres inmaterials")
	def __unicode__(self):
		if self.relation.gerund is None or self.relation.gerund == '':
			return self.nonmaterial.__unicode__()
		else:
			return self.relation.gerund+' > '+self.nonmaterial.__unicode__()


class rel_Human_Persons(models.Model):
	human = models.ForeignKey('Human', related_name='human_persons')
	person = models.ForeignKey('Person', related_name='rel_humans', verbose_name=_(u"Persona vinculada"))
	relation = TreeForeignKey('Relation', related_name='hu_hum+', blank=True, null=True, verbose_name=_(u"relació"))
	class Meta:
		verbose_name = _(u"H_per")
		verbose_name_plural = _(u"Persones vinculades")
	def __unicode__(self):
		if self.relation is None or self.relation.gerund is None or self.relation.gerund == '':
			return self.person.__unicode__()
		else:
			return self.relation.gerund+' > '+self.person.__unicode__()

	def _selflink(self):
		return self.person._selflink()
	_selflink.allow_tags = True
	_selflink.short_description = ''


class rel_Human_Projects(models.Model):
	human = models.ForeignKey('Human', related_name='human_projects')
	project = TreeForeignKey('Project', related_name='rel_humans', verbose_name=_(u"Projecte vinculat"),
		 help_text=_(u"Un cop escollit el projecte, desa el perfil per veure el seu nom aquí."))
	relation = TreeForeignKey('Relation', related_name='hu_hum+', blank=True, null=True, verbose_name=_(u"relació"))
	class Meta:
		verbose_name = _(u"H_pro")
		verbose_name_plural = _(u"Projectes vinculats")
	def __unicode__(self):
		if self.project.project_type is None or self.project.project_type == '':
			if self.relation.gerund is None or self.relation.gerund == '':
				return self.project.__unicode__()
			else:
				return self.relation.gerund+' > '+self.project.__unicode__()
		else:
			if not self.relation or self.relation.gerund is None or self.relation.gerund == '':
				return '('+self.project.project_type.being_type.name+') rel? > '+self.project.name
			else:
				return '('+self.project.project_type.being_type.name+') '+self.relation.gerund+' > '+self.project.name


class rel_Human_Companies(models.Model):
	human= models.ForeignKey('Human', related_name='human_companies')
	company = models.ForeignKey('Company', verbose_name=_(u"Empresa vinculada"))
	relation = TreeForeignKey('Relation', related_name='hu_hum+', blank=True, null=True, verbose_name=_(u"relació"))
	class Meta:
		verbose_name = _(u"H_emp")
		verbose_name_plural = _(u"Empreses vinculades")
	def __unicode__(self):
		if self.relation.gerund is None or self.relation.gerund == '':
			return self.company.__unicode__()
		else:
			return '('+self.company.company_type.being_type.name+') '+self.relation.gerund+' > '+self.company.__unicode__()



'''
class rel_Address_Jobs(models.Model):
	address = models.ForeignKey('Address')
	job = models.ForeignKey('Job', verbose_name=_(u"Art/Ofici vinculat"))
	relation = TreeForeignKey('Relation', related_name='ad_job+', blank=True, null=True)
	class Meta:
		verbose_name = _(u"job")
		verbose_name_plural = _(u"Arts/Oficis vinculats")
	def __unicode__(self):
		if self.relation.gerund is None or self.relation.gerund == '':
			return self.job.__unicode__()
		else:
			return self.relation.gerund+' > '+self.job.__unicode__()
'''



#	 A R T S - (Verbs, Relacions, Arts, Oficis, Sectors...)

class Art(MPTTModel):	# Abstract
	name = models.CharField(unique=True, max_length=200, verbose_name=_(u"Nom"), help_text=_(u"El nom de l'Art"))
	verb = models.CharField(max_length=200, blank=True, verbose_name=_(u"Verb"), help_text=_(u"El verb de la acció, infinitiu"))
	gerund = models.CharField(max_length=200, blank=True, verbose_name=_(u"Gerundi"), help_text=_(u"El verb en gerundi, present"))
	description = models.TextField(blank=True, verbose_name=_(u"Descripció"))

	parent = TreeForeignKey('self', null=True, blank=True, related_name='subarts')

	def __unicode__(self):
		if self.verb:
			return self.name+', '+self.verb
		else:
			return self.name

	class Meta:

		abstract = True

		verbose_name = _(u"Art")
		verbose_name_plural = _(u"a- Arts")


class Relation(Art):	# Create own ID's (TREE)
	#art = models.OneToOneField('Art', primary_key=True, parent_link=True)
	clas = models.CharField(blank=True, verbose_name=_(u"Clase"), max_length=50,
													help_text=_(u"Model de django o classe python associada a la Relació"))
	class Meta:
		verbose_name= _(u'Relació')
		verbose_name_plural= _(u'a- Relacions')
	def __unicode__(self):
		if self.verb:
			if self.clas is None or self.clas == '':
				return self.verb
			else:
				return self.verb+' ('+self.clas+')'
		else:
			if self.clas is None or self.clas == '':
				return self.name
			else:
				return self.name+' ('+self.clas+')'


class Job(Art):		# Create own ID's (TREE)
	#art = models.OneToOneField('Art', primary_key=True, parent_link=True)
	clas = models.CharField(blank=True, verbose_name=_(u"Clase"), max_length=50,
													help_text=_(u"Model de django o classe python associada a l'Ofici'"))

	class Meta:
		verbose_name= _(u'Ofici')
		verbose_name_plural= _(u'a- Oficis')
	def __unicode__(self):
		if self.clas is None or self.clas == '':
			return self.name#+', '+self.verb
		else:
			return self.name+' ('+self.clas+')'



#rel_tit = Relation.objects.get(clas='holder')

#	 S P A C E S - (Regions, Espais, Adreçes...)

class Space(models.Model):	# Abstact
	name = models.CharField(verbose_name=_(u"Nom"), max_length=100, help_text=_(u"El nom de l'Espai"))
	#space_type = TreeForeignKey('Space_Type', blank=True, null=True, verbose_name=_(u"Tipus d'espai"))
	#m2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

	def __unicode__(self):
		return self.name

	class Meta:
		abstract = True;

class Space_Type(Type):
	typ = models.OneToOneField('Type', primary_key=True, parent_link=True)

	class Meta:
		verbose_name= _(u"Tipus d'Espai")
		verbose_name_plural= _(u"s--> Tipus d'Espais")



class Address(Space):	# Create own ID's
	#space = models.OneToOneField('Space', primary_key=True, parent_link=True)
	address_type = TreeForeignKey('Address_Type', blank=True, null=True, verbose_name=_(u"Tipus d'adreça"))
	p_address = models.CharField(max_length=200, verbose_name=_(u"Direcció"), help_text=_(u"Adreça postal vàlida per a enviaments"))
	town = models.CharField(max_length=150, verbose_name=_(u"Població"), help_text=_(u"Poble, ciutat o municipi"))
	postalcode = models.CharField(max_length=5, blank=False, null=False, verbose_name=_(u"Codi postal"))
	region = TreeForeignKey('Region', blank=False, null=False, related_name='rel_addresses', verbose_name=_(u"Comarca"))

	#telephone = models.CharField(max_length=20, blank=True, verbose_name=_(u"Telefon fix"))
	ic_larder = models.BooleanField(default=False, verbose_name=_(u"És Rebost?"))
	#main_address = models.BooleanField(default=False, verbose_name=_(u"Adreça principal?"))
	size = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, verbose_name=_(u'Tamany'), help_text=_(u"Quantitat d'unitats (accepta 2 decimals)"))
	size_unit = models.ForeignKey('Unit', blank=True, null=True, verbose_name=_(u"Unitat de mesura"))
	longitude = models.IntegerField(blank=True, null=True, verbose_name=_(u"Longitud (geo)"))
	latitude = models.IntegerField(blank=True, null=True, verbose_name=_(u"Latitud (geo)"))

	jobs = models.ManyToManyField('Job', related_name='addresses', blank=True, null=True, verbose_name=_(u"Oficis relacionats"))

	description = models.TextField(blank=True, null=True, verbose_name=_(u"Descripció de l'Adreça"), help_text=_(u"Localització exacta, indicacions per arribar o comentaris"))

	def _main_addr_of(self):
		rel = rel_Human_Addresses.objects.filter(address=self, main_address=True).first() #TODO accept various and make a list
		if rel:
			return rel.human
		else:
			return _(u'ningú')
	_main_addr_of.allow_tags = True
	_main_addr_of.short_description = _(u"Adreça principal de")
	main_addr_of = property(_main_addr_of)


	class Meta:
		verbose_name= _(u'Adreça')
		verbose_name_plural= _(u's- Adreces')
	def __unicode__(self):
		return self.name+' ('+self.p_address+' - '+self.town+')'

	def _jobs_list(self):
		out = ul_tag
		for jo in self.jobs.all():
			out += '<li><b>'+jo.name+'</b> - '+erase_id_link('jobs', str(jo.id))+'</li>'
		if out == ul_tag:
			return str_none
		return out+'</ul>'
	_jobs_list.allow_tags = True
	_jobs_list.short_description = ''

	def _selflink(self):
		if self.id:
				return a_strG + "address/" + str(self.id) + a_str2 + a_edit +"</a>"# % str(self.id)
		else:
				return "Not present"
	_selflink.allow_tags = True

class Address_Type(Space_Type):
	space_type = models.OneToOneField('Space_Type', primary_key=True, parent_link=True)
	class Meta:
		verbose_name = _(u"Tipus d'Adreça")
		verbose_name_plural = _(u"s-> Tipus d'Adreces")



class Region(MPTTModel, Space):	# Create own ID's (TREE)
	#space = models.OneToOneField('Space', primary_key=True, parent_link=True)
	region_type = TreeForeignKey('Region_Type', blank=True, null=True, verbose_name=_(u"Tipus de regió"))
	parent = TreeForeignKey('self', null=True, blank=True, related_name='subregions')

	description = models.TextField(blank=True, null=True, verbose_name=_(u"Descripció de la Regió"))

	class Meta:
		verbose_name= _(u'Regió')
		verbose_name_plural= _(u's- Regions')

class Region_Type(Space_Type):
	space_type = models.OneToOneField('Space_Type', primary_key=True, parent_link=True)
	class Meta:
		verbose_name = _(u"Tipus de Regió")
		verbose_name_plural = _(u"s-> Tipus de Regions")




#	 A R T W O R K S - (Obres, Coses, Registres, Documents...)

class Artwork(models.Model):	# Abstract
	name = models.CharField(verbose_name=_(u"Nom"), max_length=200, blank=True, null=True) #, help_text=_(u"El nom de la obra (Registre, Unitat, Cosa)"))
	#artwork_type = TreeForeignKey('Artwork_Type', blank=True, verbose_name=_(u"Tipus d'Obra"))
	description = models.TextField(blank=True, null=True, verbose_name=_(u"Descripció"))

	def __unicode__(self):
		return self.name

	class Meta:
		abstract = True

class Artwork_Type(Type):
	typ = models.OneToOneField('Type', primary_key=True, parent_link=True)
	class Meta:
		verbose_name = _(u"Tipus d'Obra")
		verbose_name_plural = _(u"o--> Tipus d'Obres")



# - - - - - N O N - M A T E R I A L

class rel_Nonmaterial_Records(models.Model):
	nonmaterial = models.ForeignKey('Nonmaterial')
	record = models.ForeignKey('Record', verbose_name=_(u"Registre vinculat"))
	relation = TreeForeignKey('Relation', related_name='no_reg+', blank=True, null=True)
	class Meta:
		verbose_name = _(u"N_rec")
		verbose_name_plural = _(u"Registres vinculats")
	def __unicode__(self):
		if self.relation.gerund is None or self.relation.gerund == '':
			return self.record.__unicode__()
		else:
			return '('+self.record.record_type.name+') '+self.relation.gerund+' > '+self.record.__unicode__()

class rel_Nonmaterial_Addresses(models.Model):
	nonmaterial = models.ForeignKey('Nonmaterial')
	address = models.ForeignKey('Address', verbose_name=_(u"Adreça vinculada"))
	relation = TreeForeignKey('Relation', related_name='no_adr+', blank=True, null=True)
	class Meta:
		verbose_name = _(u"N_adr")
		verbose_name_plural = _(u"Adreçes vinculades")
	def __unicode__(self):
		if self.relation.gerund is None or self.relation.gerund == '':
			return self.address.__unicode__()
		else:
			return '('+self.address.address_type.name+') '+self.relation.gerund+' > '+self.address.__unicode__()

class rel_Nonmaterial_Jobs(models.Model):
	nonmaterial = models.ForeignKey('Nonmaterial')
	job = models.ForeignKey('Job', related_name='nonmaterials', verbose_name=_(u"Arts/Oficis vinculades"))
	relation = TreeForeignKey('Relation', related_name='no_job+', blank=True, null=True, verbose_name=_(u"Relació"))
	class Meta:
		verbose_name = _(u"N_ofi")
		verbose_name_plural = _(u"Arts/Oficis vinculades")
	def __unicode__(self):
		if self.relation.gerund is None or self.relation.gerund == '':
			return self.job.__unicode__()
		else:
			return self.relation.gerund+' > '+self.job.__unicode__()

class rel_Nonmaterial_Nonmaterials(models.Model):
	nonmaterial = models.ForeignKey('Nonmaterial')
	nonmaterial2 = models.ForeignKey('Nonmaterial', related_name='subnonmaterials', verbose_name=_(u"obres Inmaterials vinculades"))
	relation = TreeForeignKey('Relation', related_name='ma_mat+', blank=True, null=True, verbose_name=_(u"Relació"))
	class Meta:
		verbose_name = _(u"N_mat")
		verbose_name_plural = _(u"obres Inmaterials vinculades")
	def __unicode__(self):
		if self.relation.gerund is None or self.relation.gerund == '':
			return self.nonmaterial2.__unicode__()
		else:
			return '('+self.nonmaterial2.material_type.name+') '+self.relation.gerund+' > '+self.nonmaterial2.__unicode__()


class Nonmaterial(Artwork):	# Create own ID's
	nonmaterial_type = TreeForeignKey('Nonmaterial_Type', blank=True, null=True, verbose_name=_(u"Tipus d'obra inmaterial"))

	records = models.ManyToManyField('Record', through='rel_Nonmaterial_Records', blank=True, null=True, verbose_name=_(u"Registres relacionats"))
	addresses = models.ManyToManyField('Address', through='rel_Nonmaterial_Addresses', blank=True, null=True, verbose_name=_(u"Adreces relacionades"))
	jobs = models.ManyToManyField('Job', through='rel_Nonmaterial_Jobs', blank=True, null=True, verbose_name=_(u"Arts/Oficis relacionats"))
	nonmaterials = models.ManyToManyField('self', through='rel_Nonmaterial_Nonmaterials', symmetrical=False, blank=True, null=True, verbose_name=_(u"obres Inmaterials relacionades"))

	class Meta:
		verbose_name = _(u"Obra Inmaterial")
		verbose_name_plural = _(u"o- Obres Inmaterials")

class Nonmaterial_Type(Artwork_Type):
	artwork_type = models.OneToOneField('Artwork_Type', primary_key=True, parent_link=True)
	class Meta:
		verbose_name= _(u"Tipus d'obra Inmaterial")
		verbose_name_plural= _(u"o-> Tipus d'obres Inmaterials")



class Image(Nonmaterial):
	nonmaterial = models.OneToOneField('Nonmaterial', primary_key=True, parent_link=True)
	image = models.ImageField(upload_to='files/images', height_field='height', width_field='width',
													blank=True, null=True,
													verbose_name=_(u"Imatge (jpg/png)"))
	#footer = models.TextField(blank=True, null=True, verbose_name=_(u"Peu de foto"))
	url = models.URLField(blank=True, null=True, verbose_name=_(u"Url de la imatge"))
	height = models.IntegerField(blank=True, null=True, verbose_name=_(u"Alçada"))
	width = models.IntegerField(blank=True, null=True, verbose_name=_(u"Amplada"))

	class Meta:
		verbose_name = _(u"Imatge")
		verbose_name_plural = _(u"o- Imatges")



# - - - - - M A T E R I A L

class rel_Material_Nonmaterials(models.Model):
	material = models.ForeignKey('Material')
	nonmaterial = models.ForeignKey('Nonmaterial', verbose_name=_(u"Inmaterial vinculat"))
	relation = TreeForeignKey('Relation', related_name='ma_non+', blank=True, null=True)
	class Meta:
		verbose_name = _(u"M_inm")
		verbose_name_plural = _(u"Inmaterials vinculats")
	def __unicode__(self):
		if self.relation.gerund is None or self.relation.gerund == '':
			return self.nonmaterial.__unicode__()
		else:
			return '('+self.nonmaterial.nonmaterial_type.name+') '+self.relation.gerund+' > '+self.nonmaterial.__unicode__()

class rel_Material_Records(models.Model):
	material = models.ForeignKey('Material')
	record = models.ForeignKey('Record', verbose_name=_(u"Registre vinculat"))
	relation = TreeForeignKey('Relation', related_name='ma_reg+', blank=True, null=True)
	class Meta:
		verbose_name = _(u"M_rec")
		verbose_name_plural = _(u"Registres vinculats")
	def __unicode__(self):
		if self.relation.gerund is None or self.relation.gerund == '':
			return self.record.__unicode__()
		else:
			return '('+self.record.record_type.name+') '+self.relation.gerund+' > '+self.record.__unicode__()

class rel_Material_Addresses(models.Model):
	material = models.ForeignKey('Material')
	address = models.ForeignKey('Address', related_name='materials', verbose_name=_(u"Adreça vinculada"))
	relation = TreeForeignKey('Relation', related_name='ma_adr+', blank=True, null=True)
	class Meta:
		verbose_name = _(u"M_adr")
		verbose_name_plural = _(u"Adreçes vinculades")
	def __unicode__(self):
		if self.relation.gerund is None or self.relation.gerund == '':
			return self.address.__unicode__()
		else:
			return '('+self.address.address_type.name+') '+self.relation.gerund+' > '+self.address.__unicode__()

class rel_Material_Materials(models.Model):
	material = models.ForeignKey('Material')
	material2 = models.ForeignKey('Material', related_name='submaterials', verbose_name=_(u"obres Materials vinculades"))
	relation = TreeForeignKey('Relation', related_name='ma_mat+', blank=True, null=True, verbose_name=_(u"Relació"))
	class Meta:
		verbose_name = _(u"M_mat")
		verbose_name_plural = _(u"obres Materials vinculades")
	def __unicode__(self):
		if self.relation.gerund is None or self.relation.gerund == '':
			return self.material2.__unicode__()
		else:
			return '('+self.material2.material_type.name+') '+self.relation.gerund+' > '+self.material2.__unicode__()

class rel_Material_Jobs(models.Model):
	material = models.ForeignKey('Material')
	job = models.ForeignKey('Job', related_name='materials', verbose_name=_(u"Arts/Oficis vinculades"))
	relation = TreeForeignKey('Relation', related_name='ma_job+', blank=True, null=True, verbose_name=_(u"Relació"))
	class Meta:
		verbose_name = _(u"M_ofi")
		verbose_name_plural = _(u"Arts/Oficis vinculades")
	def __unicode__(self):
		if self.relation.gerund is None or self.relation.gerund == '':
			return self.job.__unicode__()
		else:
			return self.relation.gerund+' > '+self.job.__unicode__()


class Material(Artwork): # Create own ID's
	material_type = TreeForeignKey('Material_Type', blank=True, null=True, verbose_name=_(u"Tipus d'obra física"))

	nonmaterials = models.ManyToManyField('Nonmaterial', through='rel_Material_Nonmaterials', blank=True, null=True, verbose_name=_(u"Inmaterials relacionats"))
	records = models.ManyToManyField('Record', through='rel_Material_Records', blank=True, null=True, verbose_name=_(u"Registres relacionats"))
	addresses = models.ManyToManyField('Address', through='rel_Material_Addresses', blank=True, null=True, verbose_name=_(u"Adreces relacionades"))
	materials = models.ManyToManyField('self', through='rel_Material_Materials', symmetrical=False, blank=True, null=True, verbose_name=_(u"obres Materials relacionades"))
	jobs = models.ManyToManyField('Job', through='rel_Material_Jobs', blank=True, null=True, verbose_name=_(u"Arts/Oficis relacionats"))

	class Meta:
		verbose_name = _(u"Obra Material")
		verbose_name_plural = _(u"o- Obres Materials")

	def _addresses_list(self):
		out = ul_tag
		#print self.addresses.all()
		if self.addresses.all().count() > 0:
			for add in self.addresses.all():
				rel = add.materials.filter(material=self).first().relation
				out += '<li>'+rel.gerund+': <b>'+add.__unicode__()+'</b></li>'
			return out+'</ul>'
		return str_none
	_addresses_list.allow_tags = True
	_addresses_list.short_description = _(u"Adreçes vinculades?")

	def _jobs_list(self):
		out = ul_tag
		#print self.jobs.all()
		if self.jobs.all().count() > 0:
			for job in self.jobs.all():
				rel = job.materials.filter(material=self).first().relation
				out += '<li>'+rel.gerund+': <b>'+job.__unicode__()+'</b></li>'
			return out+'</ul>'
		return str_none
	_jobs_list.allow_tags = True
	_jobs_list.short_description = _(u"Arts/oficis vinculats?")


class Material_Type(Artwork_Type):
	artwork_type = models.OneToOneField('Artwork_Type', primary_key=True, parent_link=True)
	class Meta:
		verbose_name= _(u"Tipus d'obra Material")
		verbose_name_plural= _(u"o-> Tipus d'obres Materials")


class Asset(Material):
	material = models.OneToOneField('Material', primary_key=True, parent_link=True)
	human = models.ForeignKey('Human', verbose_name=_(u"Entitat"))
	reciprocity = models.TextField(blank=True, verbose_name=_(u"Reciprocitat"))
	class Meta:
		verbose_name = _(u"Actiu")
		verbose_name_plural = _(u"o- Actius")
	def __unicode__(self):
		return '('+self.material_type.name+') '+self.material.name

	def _selflink(self):
		if self.id:
				return a_strG + "asset/" + str(self.id) + a_str2 + a_edit +"</a>"# % str(self.id)
		else:
				return "Not present"
	_selflink.allow_tags = True
	_selflink.short_description = ''



# - - - - - U N I T S

class Unit(Artwork):	# Create own ID's
	unit_type = TreeForeignKey('Unit_Type', blank=True, null=True, verbose_name=_(u"Tipus d'Unitat"))
	code = models.CharField(max_length=4, verbose_name=_(u"Codi o Símbol"))

	region = TreeForeignKey('Region', blank=True, null=True, verbose_name=_(u"Regió d'us associada"))
	human = models.ForeignKey('Human', blank=True, null=True, verbose_name=_(u"Entitat relacionada"))

	class Meta:
		verbose_name= _(u'Unitat')
		verbose_name_plural= _(u'o- Unitats')

	def __unicode__(self):
		return self.unit_type.name+': '+self.name

class Unit_Type(Artwork_Type):
	artwork_type = models.OneToOneField('Artwork_Type', primary_key=True, parent_link=True)

	class Meta:
		verbose_name = _(u"Tipus d'Unitat")
		verbose_name_plural = _(u"o-> Tipus d'Unitats")



# - - - - - R E C O R D

class Record(Artwork):	# Create own ID's
	record_type = TreeForeignKey('Record_Type', blank=True, null=True, verbose_name=_(u"Tipus de Registre"))
	class Meta:
		verbose_name= _(u'Registre')
		verbose_name_plural= _(u'o- Registres')
	def __unicode__(self):
		if self.record_type is None or self.record_type == '':
			return self.name
		else:
			return self.record_type.name+': '+self.name

	def _selflink(self):
		if self.id:
				return a_strG + "record/" + str(self.id) + a_str2 + a_edit +"</a>"# % str(self.id)
		else:
				return "Not present"
	_selflink.allow_tags = True

class Record_Type(Artwork_Type):
	artwork_type = models.OneToOneField('Artwork_Type', primary_key=True, parent_link=True)
	class Meta:
		verbose_name= _(u'Tipus de Registre')
		verbose_name_plural= _(u'o-> Tipus de Registres')


class UnitRatio(Record):
	record = models.OneToOneField('Record', primary_key=True, parent_link=True)

	in_unit = models.ForeignKey('Unit', related_name='ratio_in', verbose_name=_(u"Unitat entrant"))
	rate = models.DecimalField(max_digits=6, decimal_places=3, verbose_name=_(u"Ratio multiplicador"))
	out_unit = models.ForeignKey('Unit', related_name='ratio_out', verbose_name=_(u"Unitat sortint"))
	class Meta:
		verbose_name = _(u"Equivalencia entre Unitats")
		verbose_name_plural = _(u"o- Equivalencies entre Unitats")
	def __unicode__(self):
		return self.in_unit.name+' * '+str(self.rate)+' = '+self.out_unit.name


class AccountCes(Record):
	record = models.OneToOneField('Record', primary_key=True, parent_link=True)

	human = models.ForeignKey('Human', related_name='accountsCes', verbose_name=_(u"Entitat humana persuaria"))
	entity = models.ForeignKey('Project', verbose_name=_(u"Xarxa del compte"))
	unit = models.ForeignKey('Unit', verbose_name=_(u"Unitat (moneda)"))
	code = models.CharField(max_length=10, blank=True, null=True, verbose_name=_(u"Codi ecoxarxa"))
	number = models.CharField(max_length=4, blank=True, null=True, verbose_name=_(u"Número compte"))

	class Meta:
		verbose_name= _(u'Compte CES')
		verbose_name_plural= _(u'o- Comptes CES')

	def __unicode__(self):
		return '('+self.unit.code+') '+self.human.nickname+' '+self.code+self.number#+' '+self.name
	def link(self):
		if self.id:
			return "/cooper/General/accountces/" + str(self.id)
		else:
			return ""
class AccountBank(Record):
	record = models.OneToOneField('Record', primary_key=True, parent_link=True)

	human = models.ForeignKey('Human', related_name='accountsBank', verbose_name=_(u"Entitat humana titular"))
	company = models.ForeignKey('Company', blank=True, null=True, verbose_name=_(u"Entitat Bancaria"))
	unit = models.ForeignKey('Unit', blank=True, null=True, verbose_name=_(u"Unitat (moneda)"))
	code = models.CharField(max_length=11, blank=True, null=True, verbose_name=_(u"Codi SWIFT/BIC"))
	number = models.CharField(max_length=34, blank=True, null=True, verbose_name=_(u"Número de Compte IBAN"))
	bankcard = models.BooleanField(default=False, verbose_name=_(u"Amb Tarjeta?"))

	class Meta:
		verbose_name= _(u'Compte Bancari')
		verbose_name_plural= _(u'o- Comptes Bancaris')

	def __unicode__(self):
		try:
			return '('+self.unit.code+') '+self.company.nickname+': '+self.human.nickname+' '+self.number	
		except:
			return "<projecte buit>"
	def link(self):
		if self.id:
			return "/cooper/General/accountbank/" + str(self.id)
		else:
			return ""
class AccountCrypto(Record):
	record = models.OneToOneField('Record', primary_key=True, parent_link=True)
	human = models.ForeignKey('Human', related_name='accountsCrypto', verbose_name=_(u"Entitat humana titular"))
	unit = models.ForeignKey('Unit', verbose_name=_(u"Unitat (moneda)"))
	number = models.CharField(max_length=34, blank=True, verbose_name=_(u"Adreça de la bitlletera"))
	class Meta:
		verbose_name = _(u"Compte Criptomoneda")
		verbose_name_plural = _(u"o- Comptes Criptomonedes")
	def __unicode__(self):
		return '('+self.unit.code+') '+self.human.nickname+' '+self.number # +' '+self.name
	def link(self):
		if self.id:
			return "/cooper/General/accountcrypto/" + str(self.id)
		else:
			return ""