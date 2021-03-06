# coding=utf-8
import re

from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager, Group
from django.utils import timezone
from django.core import validators
from django.core.mail import send_mail
from django.utils.http import urlquote

#Usuário
class Usuario(AbstractBaseUser, PermissionsMixin):
    class Meta:
        #Nome
        verbose_name = "usuario"
        verbose_name_plural = "usuários"

    #Atributos
    username = models.CharField('login', max_length=30, unique=True, help_text="Até 30 caracteres. Pode ser composto por letras, números e os caracteres '@', '.', '+', '-'  e '_'.",
        validators=[validators.RegexValidator(re.compile('^[\w.@+-]+$'), 'Digite um nome de usuário válido.', 'inválido')])
    first_name = models.CharField('nome', max_length=50, blank=True, help_text="Até 50 caracteres.")
    last_name = models.CharField('sobrenome', max_length=50, blank=True, help_text="Até 50 caracteres.")
    email = models.EmailField('email')
    is_staff = models.BooleanField('acesso ao sistema', default=False, help_text='Determina se o usuário pode acessar o sistema de gerenciamento de extintores.')
    is_active = models.BooleanField('ativo', default=True, help_text='Determina se o usuário está ativo.')
    date_joined = models.DateTimeField('data de cadastro', default=timezone.now)
    matricula = models.DecimalField("matricula", default=0, max_digits=15, decimal_places=0, blank=True, help_text="Até 15 digitos numéricos.")
    funcao = models.CharField("função", max_length=50, help_text="Até 50 caracteres.")
    cpf = models.DecimalField("CPF", max_digits=11, decimal_places=0, help_text="CPF do usuário, somente números.")

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'funcao', 'cpf']

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.username)

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    #Nome do objeto
    def __unicode__(self):
        return self.username

#Grupo
descricao = models.CharField("descrição", max_length=100, blank=True)
descricao.contribute_to_class(Group, 'descricao')

class Grupo(Group):
    class Meta:
        proxy = True


#Unidade organizacional
class UnidadeOrganizacional(models.Model):
    class Meta:
        #Nome
        verbose_name = "Unidade Organizacional"
        verbose_name_plural = "Unidades Organizacionais"

    #Atributos
    nome = models.CharField("nome", max_length=50, unique=True , help_text="Nome alfanumérico de até 50 caracteres.")
    descricao = models.CharField("descrição", max_length=100, blank=True)
    responsavel = models.CharField("responsável", max_length=50, blank=True)
    telefone = models.DecimalField("telefone", max_digits=15, decimal_places=0, blank=True, help_text="Até 15 digitos numéricos.")
    anotacoes = models.TextField("anotações", max_length=500, blank=True)

    #Nome do objeto
    def __unicode__(self):
        return self.nome


#Localização
class Localizacao(models.Model):
    class Meta:
        #Nome
        verbose_name = "Localização"
        verbose_name_plural = "Localizações"

    #Listas
    TIPO = (
        ("CORREDOR", "Corredor"),
        ("SALA", "Sala"),
    )

    #Atributos
    unidade = models.ForeignKey('UnidadeOrganizacional', on_delete=models.PROTECT,
                                help_text="Unidade Organizacional a que pertence")
    codigo = models.CharField("código", max_length=10, unique=True, help_text="Até 10 caracteres alfanuméricos.")
    nome = models.CharField("nome", max_length=50, unique=True, help_text="Até 50 caracteres alfanuméricos.")
    descricao = models.CharField("descrição", max_length=100)
    telefone = models.DecimalField("telefone", max_digits=15, decimal_places=0, blank=True,
                                   help_text="Até 15 digitos númericos.")
    bloco = models.CharField("bloco", max_length=10, help_text="Bloco onde se encontra. Até 10 digitos alfanuméricos.")
    tipo = models.CharField("tipo", max_length=10, choices=TIPO)
    numero = models.CharField("número", max_length=10, blank=True, help_text="Até 10 digitos alfanuméricos.")
    andar = models.DecimalField("andar", max_digits=2, decimal_places=0)
    risco = models.DecimalField("risco", max_digits=1, decimal_places=0, blank=True,
                                help_text="Único número indicando análise de risco.")
    anotacoes = models.TextField("anotações", max_length=500, blank=True)

    #Nome do objeto
    def __unicode__(self):
        return self.nome


#Tipo de Extintor
class TipoDeExtintor(models.Model):
    class Meta:
        #Nome
        verbose_name = "Tipo de Extintor"
        verbose_name_plural = "Tipos de Extintor"

    #Listas
    MEDIDA = (
        ("LITRO", "L"),
        ("KILOGRAMA","Kg")
    )

    #Atributos
    codigo = models.CharField("código", max_length=10, unique=True,
                              help_text="Identificador de tipo de até 10 caracteres alfanuméricos.")
    descricao = models.CharField("descrição", max_length=50)
    unidade = models.CharField("unidade de medida da capacidade", max_length=10, choices=MEDIDA,
                               help_text="Unidade de medida do conteúdo do extintor")

    #Nome do objeto
    def __unicode__(self):
        return self.codigo


#Extintor
class Extintor(models.Model):
    class Meta:
        #Nome
        verbose_name = "Extintor"
        verbose_name_plural = "Extintores"

    #Listas
    USO = (
        ("PADRAO", "Padrão"),
        ("COBERTURA", "Cobertura"),
    )

    #Atributos
    carcaca = models.CharField("número da carcaça", max_length=10, blank=True, unique=True,
                               help_text="Até 10 digitos númericos.")
    codigo = models.DecimalField("código interno", max_digits=4, decimal_places=0, unique=True,
                                 help_text="Exatamente 4 digitos númericos.")
    tipo = models.ForeignKey('TipoDeExtintor', on_delete=models.PROTECT)
    capacidade = models.DecimalField("capacidade", max_digits=6, decimal_places=3,
                                     help_text="Até 6 digitos númericos.")
    localizacao = models.ForeignKey('Localizacao', on_delete=models.PROTECT)
    uso = models.CharField("descrição", max_length=20, choices=USO)
    troca = models.BooleanField("troca de peças", help_text="Se houve troca ou não.")
    data_fabricacao = models.DateField("data de fabricação", blank=True)
    data_recarga = models.DateField("data da última recarga", blank=True)
    data_reteste = models.DateField("data do último reteste", blank=True)
    validade_recarga = models.DateField("validade da recarga", blank=True)
    validade_reteste = models.DateField("validade do reteste", blank=True)
    observacoes = models.TextField("observações", max_length=250, blank=True)
    anotacoes = models.TextField("anotações", max_length=500, blank=True)

    #Nome do objeto
    def __unicode__(self):
        return str(self.carcaca)


#Extintor Inativo
class ExtintorInativo(models.Model):
    class Meta:
        #Nome
        verbose_name = "Extintor inativo"
        verbose_name_plural = "Extintores inativos"

    #Listas
    MOTIVO = (
        ("REPROVADO_RETESTE", "Reprovado por reteste"),
        ("EXTRAVIADO", "Extraviado"),
        ("OUTRO", "Outro"),
    )

    #Atributos
    extintor = models.OneToOneField('Extintor', related_name='inativo', on_delete=models.PROTECT)
    motivo = models.CharField("motivo", max_length=20, choices=MOTIVO)
    data = models.DateField("data de desativação", auto_now_add=True)
    comentarios = models.TextField("comentários", max_length=250, blank=True)

    #Nome do objeto
    def __unicode__(self):
        return str(self.extintor.carcaca)


#Extintor Emprestado
class ExtintorEmprestado(models.Model):
    class Meta:
        #Nome
        verbose_name = "Extintor emprestado"
        verbose_name_plural = "Extintores emprestados"

    #Atributos
    extintor = models.OneToOneField('Extintor', related_name='emprestado', on_delete=models.PROTECT)
    inicio = models.DateField("data do empréstimo")
    devolucao = models.DateField("data para devolução", blank=True)
    responsavel = models.CharField("responsável", max_length=50,
                                   help_text="Responsável pelos extintores emprestados.")
    telefone = models.DecimalField("telefone", max_digits=15, decimal_places=0, blank=True,
                                   help_text="Até 15 digitos numéricos.")
    comentarios = models.TextField("comentários", max_length=250, blank=True)

    #Nome do objeto
    def __unicode__(self):
        return str(self.extintor.carcaca)

#Extintor com Recarga Necessária
class ExtintorRecargaNecessaria(models.Model):
    class Meta:
        #Nome
        verbose_name = "Extintor com necessidade de recarga"
        verbose_name_plural = "Extintores com necessidade de recarga"

    #Listas
    MOTIVO = (
        ("VENCIMENTO", "Recarga vencida"),
        ("AVARIA", "Avaria"),
        ("OUTRO", "Outro"),
    )

    #Atributos
    extintor = models.OneToOneField('Extintor', related_name='recarga_necessaria', on_delete=models.PROTECT)
    motivo = models.CharField("motivo", max_length=20, choices=MOTIVO)
    comentarios = models.TextField("comentários", max_length=250, blank=True)

    #Nome do objeto
    def __unicode__(self):
        return str(self.extintor.carcaca)


#Recarga
class Recarga(models.Model):
    class Meta:
        #Nome
        verbose_name = "operação de recarga"
        verbose_name_plural = "operações de recarga"

    #Atributos
    identificador = models.CharField("identificador", max_length=50, blank=True,
                                     help_text="Identificador de até 50 caracteres alfanuméricos.")
    extintores = models.ManyToManyField('Extintor', related_name='recarga', limit_choices_to={'recarga_necessaria__isnull': False})
    data_saida = models.DateField("data de saída")
    observacoes = models.TextField("observações", max_length=250, blank=True)

    #Nome do objeto
    def __unicode__(self):
        return self.identificador

#Recarga Concluída
class RecargaConcluida(models.Model):
    class Meta:
        #Nome
        verbose_name = "operação de recarga concluída"
        verbose_name_plural = "operações de recarga concluídas"

    #Atributos
    recarga = models.OneToOneField('Recarga', related_name='recarga_concluida', on_delete=models.PROTECT,
                                   help_text="Extintores que foram recarregados.")
    reteste = models.ManyToManyField('Extintor', related_name='reteste+', help_text="Extintores que foram retestados.", limit_choices_to={'recarga_necessaria__isnull': False}, blank=True)
    perdas = models.ManyToManyField('Extintor', related_name='perdas+', help_text="Extintores que foram desativados.", limit_choices_to={'recarga_necessaria__isnull': False}, blank=True)
    trocas = models.ManyToManyField('Extintor', related_name='trocas+', help_text="Extintores que sofreram troca de peças.", limit_choices_to={'recarga_necessaria__isnull': False}, blank=True)
    data_chegada = models.DateField("data de chegada")
    observacoes = models.TextField("observações", max_length=250, blank=True)

    #Nome do objeto
    def __unicode__(self):
        return self.recarga.identificador

    def save(self, *args, **kwargs):
        super(RecargaConcluida, self).save(*args, **kwargs)

        for ex in self.recarga.extintores.all():
            ex.data_recarga = self.data_chegada
            ex.validade_recarga = ex.validade_reteste + timedelta(days=365)
            ex.save()
            ExtintorRecargaNecessaria.objects.filter(extintor=ex).delete()

        for ex in self.recarga.recarga_concluida.reteste.all():
            ex.data_reteste = self.data_chegada
            ex.validade_reteste = ex.validade_reteste + timedelta(days=365*5)
            ex.save()

        for ex in self.recarga.recarga_concluida.perdas.all():
            ex_perda = ExtintorInativo.objects.create(data=self.data_chegada, motivo='REPROVADO_RETESTE', extintor=ex)
            ex_perda.save()

        for ex in self.recarga.recarga_concluida.trocas.all():
            ex.troca = True
            ex.save()

    #Modificar formulário para restringir opções de reteste e perda de acordo com o conjunto original

#Substituição
class Substituicao(models.Model):
    class Meta:
        #Nome
        verbose_name = "substituição"
        verbose_name_plural = "substituições"

    #Atributos
    identificador = models.CharField("identificador", max_length=50, blank=True)
    data = models.DateField("data")
    motivo = models.CharField("motivo", max_length=50)
    origem = models.ForeignKey('Localizacao', related_name='substituicao_origem',
                               help_text="Localização de origem.")
    destino = models.ForeignKey('Localizacao', related_name='substituicao_destino',
                                help_text="Localização de destino.")
    extintores = models.ManyToManyField('Extintor', related_name='substituicao',
                                        help_text="Extintores substituidos.")
    cobertura = models.ManyToManyField('Extintor', related_name='cobertura',
                                       help_text="Extintores de cobertura utilizados.")
    observacoes = models.TextField("observações", max_length=250, blank=True)

    #Nome do objeto
    def __unicode__(self):
        return self.identificador

    #Incluir validação para os grupos de extintores, e mudanças de localização
    #Incluir validação para local do extintor
    #Definir para onde vai o extintor substituido



#Notificação



#Histórico de Usuário



#Histórico de Extintor



#Vistoria



#Custo





