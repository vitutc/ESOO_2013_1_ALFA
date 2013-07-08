# coding=utf-8
from django.contrib import admin
from django.contrib.auth.models import Permission
from Extintor.models import *


#Configuração de "inlines"
class ExtintorRecargaNecessariaInline(admin.StackedInline):
    model = ExtintorRecargaNecessaria
    extra = 0
    max_num = 1
    verbose_name = 'Informar necessidade de recarga'
    verbose_name_plural = 'Informar necessidade de recarga'
    inline_classes = ('grp-collapse grp-open')

class ExtintorEmprestadoInline(admin.StackedInline):
    model = ExtintorEmprestado
    extra = 0
    max_num = 1
    verbose_name = 'Cadastrar empréstimo'
    verbose_name_plural = 'Cadastrar empréstimo'
    inline_classes = ('grp-collapse grp-open')

class ExtintorInativoInline(admin.StackedInline):
    model = ExtintorInativo
    extra = 0
    max_num = 1
    verbose_name = 'Desativar extintor'
    verbose_name_plural = 'Desativar extintor'
    inline_classes = ('grp-collapse grp-open')

class ExtintorAdmin(admin.ModelAdmin):
    inlines = [ExtintorRecargaNecessariaInline, ExtintorEmprestadoInline, ExtintorInativoInline]
    #search_fields = ['','']

#Registrar modelos na interface administrativa
admin.site.register(Extintor, ExtintorAdmin)
admin.site.register(UnidadeOrganizacional)
admin.site.register(Localizacao)
admin.site.register(TipoDeExtintor)
admin.site.register(Recarga)
#admin.site.register(Permission) #Ativar a linha para editar texto de permissões, depois desativar.