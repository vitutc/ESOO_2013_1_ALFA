# coding=utf-8
from django.contrib import admin
from django.contrib.auth.models import Permission
from django.forms import TextInput
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
    search_fields = ['localizacao__unidade__nome', 'carcaca', 'uso', 'tipo__unidade',
                     'tipo__codigo', 'localizacao__codigo', 'localizacao__nome', 'localizacao__tipo',
                     'localizacao__bloco']
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'20'})}, #tamanho arbitrario
        #models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    }

    # limitar o tamanho da caixa de numero de carcaça

class LocalizacaoAdmin(admin.ModelAdmin):
    pass
    #formfield_overrides = {
    #    models.CharField: {'widget': TextInput(attrs={'size':'20'})}, #tamanho arbitrario
    #    #models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    #}

#Registrar modelos na interface administrativa
admin.site.register(Extintor, ExtintorAdmin)
admin.site.register(UnidadeOrganizacional)
admin.site.register(Localizacao, LocalizacaoAdmin)
admin.site.register(TipoDeExtintor)
admin.site.register(Recarga)
#admin.site.register(Permission) #Ativar a linha para editar texto de permissões, depois desativar.