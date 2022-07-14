from asyncore import write
from django.http import Http404, HttpResponse, HttpResponseForbidden
from medicos.serializers import MedicoSerializer
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Usuario
from medicos.models import Medico
import ipdb


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["id" ,"nome", "email", "is_active", "password", "criado_em", "atualizado_em"]
        extra_kwargs = {
            "password": {"write_only": True},
            "criado_em": {"read_only": True},
            "atualizado_em": {"read_only": True},
        }
    
    def to_representation(self, instance):
        return {
            "id": instance.id,
            "nome": instance.nome,
            "email": instance.email,
            "ativo": instance.is_active,
            "criado_em": instance.criado_em,
            "atualizado_em": instance.atualizado_em,
        }
    
    def create(self, validated_data):
        return Usuario.objects.criar_usuario(**validated_data)


class UsuarioMedicoSerializer(serializers.ModelSerializer):
    medico = MedicoSerializer(read_only=True)
    especialidade = serializers.CharField(write_only=True)
    registro_profissional = serializers.CharField(write_only=True)
    telefone = serializers.CharField(write_only=True)
    class Meta:
        model = Usuario
        fields = [
            "id" , "nome", "email",
            "password", "especialidade",
            "telefone", "medico",
            "registro_profissional",
            "criado_em", "atualizado_em"
        ]
        extra_kwargs = {
            "id":{"read_only": True},
            "password": {"write_only": True},
            "criado_em": {"read_only": True},
            "atualizado_em": {"read_only": True},
        }

    def create(self, validated_data):
        medico_data = {
            "especialidade": validated_data.pop("especialidade"),
            "registro_profissional": validated_data.pop("registro_profissional"),
            "telefone": validated_data.pop("telefone")
        }
        serializer = MedicoSerializer(data=medico_data)
        serializer.is_valid(raise_exception=True)
        usuario =  Usuario.objects.criar_agente_de_saude(**validated_data)
        Medico.objects.create(**serializer.validated_data, usuario=usuario)
        return usuario
    
    def update(self, instance, validated_data):
        instance.nome = validated_data.get("nome", instance.nome)
        instance.email = validated_data.get("email", instance.email)
        if(
            "especialidade" in validated_data or
            "registro_profissional" in validated_data or
            "telefone" in validated_data
        ):
            instance.medico.especialidade = validated_data.get("especialidade", instance.medico.especialidade)
            instance.medico.registro_profissional = validated_data.get("registro_profissional", instance.medico.registro_profissional)
            instance.medico.telefone = validated_data.get("telefone", instance.medico.telefone)

        instance.save()
        return instance


class UsuarioProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True}
        }


class ChangeActivePropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}

    def update(self, instance, validated_data):
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.save()
        return instance
