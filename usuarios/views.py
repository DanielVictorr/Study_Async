from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import  messages
from django.contrib import auth

def cadastro (request):
    if request.method == "GET":
        return render(request, 'cadastro.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        if not senha == confirmar_senha:
            messages.add_message(request, constants.ERROR, 'As senhas não coincidem')
            return redirect('/usuarios/cadastro')
        
        user = User.objects.filter(username=username)
        
        if user.exists():
            messages.add_message(request, constants.ERROR, 'Usuário já existe')
            return redirect('/usuarios/cadastro')

        try:
            User.objects.create_user(
                username=username,      #a esquerda do = esta o nome da coluna da tabela e a direita é o valor que é digitado no input pelo user
                password=senha
            )
            messages.add_message(request, constants.ERROR, 'Usuário cadastrado com sucesso')
            return redirect('/usuarios/login')
        except:
            messages.add_message(request, constants.ERROR, 'Erro no servidor')
            return redirect('/usuarios/cadastro')

def logar (request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = auth.authenticate(request, username=username, password=senha)

        if user:
            auth.login(request, user)
            messages.add_message(request, constants.SUCCESS, 'Logado!')
            return redirect('/flashcard/novo_flashcard') # não foi criado ainda

        else:
            messages.add_message(request, constants.ERROR, 'Usuário ou senha inválidos!')
            return redirect('/usuarios/logar')

def logout(request):
    auth.logout(request)
    return redirect('/usuarios/logar')