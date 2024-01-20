function flip_card(id){
    // puxa o elemento pelo id
    card = document.getElementById(id) 

    if (card.style.display == 'none' || card.style.display == ''){
        card.style.display = 'block' 
        // block torna as respostas visiveis
    }
    else {
        card.style.display = 'none' 
    }
}