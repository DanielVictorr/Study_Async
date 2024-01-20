from django.http import HttpResponse
from django.shortcuts import redirect, render
from .models import Categoria, Flashcard, Desafio, FlashcardDesafio #models represeta as tabelas do banco
from django.contrib.messages import constants
from  django.contrib import messages, auth

# Create your views here.
def novo_flashcard(request):
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')
    if request.method == 'GET':
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        categorias = Categoria.objects.all()
        flashcards = Flashcard.objects.filter(user = request.user)

        categoria_filtrar = request.GET.get('categoria') # dentro dos parenteses fica o nome do selct no html
        dificuldade_filtrar = request.GET.get('dificuldade')

        if categoria_filtrar:
            flashcards = flashcards.filter(categoria__id = categoria_filtrar)

        if dificuldade_filtrar:
            flashcards = flashcards.filter(dificuldade = dificuldade_filtrar)

        # render envia informação do banco para o arquivo html
        return render (request, 'novo_flashcard.html', {'categorias': categorias,
                                                        'dificuldades': dificuldades,
                                                          'flashcards': flashcards})
    
    elif request.method == "POST":
        pergunta = request.POST.get('pergunta')
        resposta = request.POST.get('resposta')
        categoria = request.POST.get('categoria')
        dificuldade = request.POST.get('dificuldade')

        if len(pergunta.strip()) == 0 or len(resposta.strip()) == 0: ##strip apaga excesso de espaço antes ou depois de palavras
            messages.add_message(request, constants.ERROR, "Preencha os campos de pergunta e resposta")
            return redirect('/flashcard/novo_flashcard/')

        flashcard = Flashcard(
            user = request.user,
            pergunta = pergunta,
            resposta = resposta,
            categoria_id = categoria,
            dificuldade = dificuldade,
        )

        flashcard.save()

        messages.add_message(request, constants.SUCCESS, "Flashcard cadastrado com sucesso.")
        return redirect('/flashcard/novo_flashcard/')

def deletar_flashcard(request, id):
    # Fazer validação de segurança
    # Utilizar o request.user
    # Se o id do flashcard não for do user logado, faça: você não tem permissão para deletar esse flashcard tentar excluir 6
    
    flashcard = Flashcard.objects.get(id = id)
    flashcard.delete()

    messages.add_message(request, constants.SUCCESS, 'Flashcard deletado com sucesso!')

    return redirect('/flashcard/novo_flashcard/')


def iniciar_desafio(request):
    if request.method == "GET":
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        categorias = Categoria.objects.all()
        return render(request, 'iniciar_desafio.html', {'categorias': categorias,
                                                        'dificuldades': dificuldades}) #terceiro parametro da render envia para o html
    
    elif request.method == "POST":
        titulo = request.POST.get('titulo')
        categorias = request.POST.getlist('categoria') #getlist porque no html o select é multiple e sempre que temos um multiplo envio de dados temos que usar o getlist
        dificuldade = request.POST.get('dificuldade')
        qtd_perguntas = request.POST.get('qtd_perguntas')

        desafio = Desafio(
            user = request.user,
            titulo = titulo,
            quantidade_perguntas = qtd_perguntas,
            dificuldade = dificuldade,
        )

        desafio.save()

        # desafio.categoria.add(*categorias) ##outra maneira de pegar multiplas categorias fazendo o python rodar o for internamente

        for categoria in categorias:
            desafio.categoria.add() # adiciona multiplas categorias ao desafio

        flashcards = (
            Flashcard.objects.filter(user = request.user)
            .filter(dificuldade = dificuldade)
            .filter(categoria_id__in = categorias) # filtra as categorias onde o id esta em uma lista de categorias _id__in
            .order_by('?') #função do django que traz os flashcards de forma aleatória
        )
        
        
        # print(flashcards.count())
        if flashcards.count() < int(qtd_perguntas):
            messages.add_message(request, constants.ERROR, 'Qts questões maior que a quantidade de flashcards. Coloque uma Qtd questões menor e tente novamente!')
            desafio.delete()
            return redirect('/flashcard/iniciar_desafio/')
            # Tratar para escolher depois
            #Se estiver menos flashcard do que pergunta vai dar erro!
            # Tentar fazer solito
            

        
        flashcards = flashcards[: int(qtd_perguntas)]
        
        

        for f in flashcards:
            flashcard_desafio = FlashcardDesafio(
                flashcard = f
            )

            flashcard_desafio.save()
            desafio.flashcards.add(flashcard_desafio)

        desafio.save()

        return redirect(f'/flashcard/listar_desafio')

def listar_desafio(request):
    desafios = Desafio.objects.filter(user = request.user)
    categorias = Categoria.objects.all()
    dificuldades = Flashcard.DIFICULDADE_CHOICES
    # desenvolver status. O que é o status? Desafios respondidos!
    # desenvolver filtros
    return render(request, 'listar_desafio.html',{'desafios': desafios, 'categorias': categorias, 'dificuldades': dificuldades})


def desafio(request, id):
    desafio = Desafio.objects.get(id = id)
    
    if not desafio.user == request.user:
        messages.add_message(request, constants.ERROR, 'Você não tem permissão para responder este desafio!')
        return redirect(f'/flashcard/listar_desafio/')

    if request.method == 'GET':
        acertos = desafio.flashcards.filter(respondido = True).filter(acertou = True).count()
        erros = desafio.flashcards.filter(respondido = True).filter(acertou = False).count()
        faltantes = desafio.flashcards.filter(respondido = False).count()
        return render(request,'desafio.html', {'desafio': desafio, 'acertos': acertos, 'erros': erros, 'faltantes': faltantes})

    

def responder_flashcard(request, id):
    flashcard_desafio = FlashcardDesafio.objects.get(id = id)
    acertou = request.GET.get('acertou')
    desafio_id = request.GET.get('desafio_id')

    if not flashcard_desafio.flashcard.user == request.user:
        messages.add_message(request, constants.ERROR, 'Você não tem permissão para responder este desafio!')
        return redirect(f'/flashcard/desafio/{desafio_id}')

    flashcard_desafio.respondido = True
    

    # flashcard_desafio.acertou = True if acertou == "1" else False

    if acertou == "1":
        flashcard_desafio.acertou = True
    elif acertou == "0":
        flashcard_desafio.acertou = False

    flashcard_desafio.save()
    return redirect(f'/flashcard/desafio/{desafio_id}')





        
