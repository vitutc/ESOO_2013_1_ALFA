# coding=utf-8
from django.contrib import admin
from django.forms import TextInput
from django.contrib.sites.models import Site

from django.db import transaction
from django.conf import settings
from forms import UserCreationForm, UserChangeForm, AdminPasswordChangeForm
from django.contrib.auth.models import Group
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.html import escape
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
csrf_protect_m = method_decorator(csrf_protect)

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

    #Exibição de lista
    list_display = ['carcaca', 'uso', 'codigo', 'get_unidade', 'get_capacidade', 'get_tipo', 'get_localizacao']

    def get_unidade(self, obj):
        return '%s'%(obj.localizacao.unidade.nome)
    get_unidade.short_description = 'Unidade Organizacional'

    def get_capacidade(self, obj):
        return '%s %s'%(obj.capacidade, dict(TipoDeExtintor.MEDIDA)[obj.tipo.unidade])
    get_capacidade.short_description = 'Capacidade'

    def get_tipo(self, obj):
        return '%s'%(obj.tipo.codigo)
    get_tipo.short_description = 'Tipo'

    def get_localizacao(self, obj):
        return '%s - %s. %s, %s %s'%(obj.localizacao.codigo, obj.localizacao.nome, dict(Localizacao.TIPO)[obj.localizacao.tipo], obj.localizacao.bloco, obj.localizacao.numero)
    get_localizacao.short_description = 'Localização'

    #Overrides no formulário
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

    #Exibição de lista
    list_display = ['get_unidade', 'nome', 'tipo', 'codigo', 'bloco']

    def get_unidade(self, obj):
        return '%s'%(obj.unidade.nome)
    get_unidade.short_description = 'Unidade Organizacional'


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

class GrupoAdmin(admin.ModelAdmin):
    search_fields = ('name', 'descricao')
    ordering = ('name', 'descricao')
    filter_horizontal = ('permissions',)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'permissions':
            qs = kwargs.get('queryset', db_field.rel.to.objects)
            # Avoid a major performance hit resolving permission names which
            # triggers a content_type load:
            kwargs['queryset'] = qs.select_related('content_type')
        return super(GrupoAdmin, self).formfield_for_manytomany(
            db_field, request=request, **kwargs)

class UsuarioAdmin(admin.ModelAdmin):
    add_form_template = 'admin/auth/user/add_form.html'
    change_user_password_template = None
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'cpf', 'matricula', 'funcao')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'cpf', 'funcao')}
        ),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'cpf', 'matricula', 'funcao', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'cpf', 'matricula', 'funcao')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super(UsuarioAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults.update({
                'form': self.add_form,
                'fields': admin.util.flatten_fieldsets(self.add_fieldsets),
            })
        defaults.update(kwargs)
        return super(UsuarioAdmin, self).get_form(request, obj, **defaults)

    def get_urls(self):
        from django.conf.urls import patterns
        return patterns('',
            (r'^(\d+)/password/$',
             self.admin_site.admin_view(self.user_change_password))
        ) + super(UsuarioAdmin, self).get_urls()

    def lookup_allowed(self, lookup, value):
        # See #20078: we don't want to allow any lookups involving passwords.
        if lookup.startswith('password'):
            return False
        return super(UsuarioAdmin, self).lookup_allowed(lookup, value)

    @sensitive_post_parameters()
    @csrf_protect_m
    @transaction.commit_on_success
    def add_view(self, request, form_url='', extra_context=None):
        # It's an error for a user to have add permission but NOT change
        # permission for users. If we allowed such users to add users, they
        # could create superusers, which would mean they would essentially have
        # the permission to change users. To avoid the problem entirely, we
        # disallow users from adding users if they don't have change
        # permission.
        if not self.has_change_permission(request):
            if self.has_add_permission(request) and settings.DEBUG:
                # Raise Http404 in debug mode so that the user gets a helpful
                # error message.
                raise Http404(
                    'Your user does not have the "Change user" permission. In '
                    'order to add users, Django requires that your user '
                    'account have both the "Add user" and "Change user" '
                    'permissions set.')
            raise PermissionDenied
        if extra_context is None:
            extra_context = {}
        username_field = self.model._meta.get_field(self.model.USERNAME_FIELD)
        defaults = {
            'auto_populated_fields': (),
            'username_help_text': username_field.help_text,
        }
        extra_context.update(defaults)
        return super(UsuarioAdmin, self).add_view(request, form_url,
                                               extra_context)

    @sensitive_post_parameters()
    def user_change_password(self, request, id, form_url=''):
        if not self.has_change_permission(request):
            raise PermissionDenied
        user = get_object_or_404(self.queryset(request), pk=id)
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                msg = ugettext('Password changed successfully.')
                messages.success(request, msg)
                return HttpResponseRedirect('..')
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Change password: %s') % escape(user.get_username()),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': '_popup' in request.REQUEST,
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
        }
        return TemplateResponse(request,
            self.change_user_password_template or
            'admin/auth/user/change_password.html',
            context, current_app=self.admin_site.name)

    def response_add(self, request, obj, post_url_continue=None):
        """
        Determines the HttpResponse for the add_view stage. It mostly defers to
        its superclass implementation but is customized because the User model
        has a slightly different workflow.
        """
        # We should allow further modification of the user just added i.e. the
        # 'Save' button should behave like the 'Save and continue editing'
        # button except in two scenarios:
        # * The user has pressed the 'Save and add another' button
        # * We are adding a user in a popup
        if '_addanother' not in request.POST and '_popup' not in request.POST:
            request.POST['_continue'] = 1
        return super(UsuarioAdmin, self).response_add(request, obj,
                                                   post_url_continue)


#Registrar modelos na interface administrativa
admin.site.register(Extintor, ExtintorAdmin)
admin.site.register(UnidadeOrganizacional, UnidadeOrganizacionalAdmin)
admin.site.register(Localizacao, LocalizacaoAdmin)
admin.site.register(TipoDeExtintor, TipoDeExtintorAdmin)
admin.site.register(Recarga, RecargaAdmin)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Grupo, GrupoAdmin)

admin.site.unregister(Group)
admin.site.unregister(Site)
#admin.site.register(Permission) #Ativar a linha para editar texto de permissões, depois desativar.