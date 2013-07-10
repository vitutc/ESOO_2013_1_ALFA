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
    # Criterios de busca:
    #   Nome da Unidade Organizacional
    #   Numero da Carcaca
    #   Se e Padrao ou de Cobertura
    #   Unidade de Medida (L ou Kg)
    #   Tipo de Extintor
    #   Codigo da Localizacao
    #   Nome da Localizacao
    #   Tipo da Localizacao (Corredor ou Sala)
    #   Bloco da Localizacao

    search_fields = ['localizacao__unidade__nome', 'carcaca', 'uso', 'tipo__unidade',
                     'tipo__codigo', 'localizacao__codigo', 'localizacao__nome', 'localizacao__tipo',
                     'localizacao__bloco']
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'20'})}, #tamanho arbitrario
        #models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    }

    # limitar o tamanho da caixa de numero de carcaça

class LocalizacaoAdmin(admin.ModelAdmin):
    # Criterios de busca:
    #   Nome da Unidade Organizacional
    #   Nome da Localizacao
    #   Tipo da Localizacao (Corredor ou Sala)
    #   Bloco da Localizacao
    #   Codigo da Localizacao

    search_fields = ['unidade__nome', 'nome', 'tipo', 'codigo', 'bloco']
    #formfield_overrides = {
    #    models.CharField: {'widget': TextInput(attrs={'size':'20'})}, #tamanho arbitrario
    #    #models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    #}

class UnidadeOrganizacionalAdmin(admin.ModelAdmin):
    # Criterios de busca:
    #   Nome da Unidade Organizacional
    #   Responsavel

    search_fields = ['nome', 'responsavel']

class TipoDeExtintorAdmin(admin.ModelAdmin):
    # Criterios de busca:
    #   Codigo do Tipo(nome)
    #   Unidade de Medida (Kg ou L)

    search_fields = ['codigo', 'unidade']

class RecargaAdmin(admin.ModelAdmin):
    # Criterios de busca:
    #   Identificador da Recarga
    #   Extintores Contidos na Recarga: Codigo da Carcaca, Tipo de Extintor, Nome da Localizacao do Extintor

    search_fields = ['identificador', 'extintores__carcaca', 'extintores__tipo__codigo', 'extintores__localizacao__nome']


#Registrar modelos na interface administrativa
admin.site.register(Extintor, ExtintorAdmin)
admin.site.register(UnidadeOrganizacional, UnidadeOrganizacionalAdmin)
admin.site.register(Localizacao, LocalizacaoAdmin)
admin.site.register(TipoDeExtintor, TipoDeExtintorAdmin)
admin.site.register(Recarga, RecargaAdmin)
admin.site.register(Usuario)
#admin.site.register(Permission) #Ativar a linha para editar texto de permissões, depois desativar.