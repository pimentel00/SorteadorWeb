from flask import Flask, render_template, request, redirect, flash, session
import random

app = Flask(__name__)
app.secret_key = 'chave_secreta_sorteador' 

NIVEIS_NOME = {
    1: "Ruim",
    2: "Decente",
    3: "Técnico",
    4: "Veloz"
}

def realizar_sorteio(num_times, tamanho_time, lista_jogadores):
    total_necessario = num_times * tamanho_time
    if len(lista_jogadores) < total_necessario:
        return None, f"ERRO: Faltam {total_necessario - len(lista_jogadores)} jogadores para o sorteio."

    pesos = {3: 40, 4: 30, 2: 20, 1: 10}

    jogadores_misturados = list(lista_jogadores)
    random.shuffle(jogadores_misturados)

    jogadores_ordenados = sorted(jogadores_misturados, key=lambda j: pesos[j['nivel']], reverse=True)

    times_info = [{'jogadores': [], 'pontos': 0} for _ in range(num_times)]

    for jogador in jogadores_ordenados:
        peso_jogador = pesos[jogador['nivel']]
        
        times_com_vaga = [t for t in times_info if len(t['jogadores']) < tamanho_time]
        if not times_com_vaga:
            break
            
        times_com_vaga.sort(key=lambda t: (t['pontos'], len(t['jogadores'])))
        time_escolhido = times_com_vaga[0]
        time_escolhido['jogadores'].append(jogador)
        time_escolhido['pontos'] += peso_jogador

    return times_info, None

@app.route('/')
def index():
    # Puxa a lista apenas da sessão (navegador) de quem está acessando
    jogadores = session.get('jogadores', [])
    return render_template('index.html', jogadores=jogadores, niveis=NIVEIS_NOME)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    nome = request.form.get('nome').strip().title()
    nivel = int(request.form.get('nivel'))
    
    jogadores = session.get('jogadores', [])
    
    if nome:
        # Cria um ID único baseado no tamanho da lista do usuário
        novo_id = 1 if not jogadores else max(j['id'] for j in jogadores) + 1
        jogadores.append({'id': novo_id, 'nome': nome, 'nivel': nivel})
        
        # Salva a lista atualizada de volta na sessão do usuário
        session['jogadores'] = jogadores
        session.modified = True 
        
    return redirect('/')

@app.route('/excluir/<int:id_jog>')
def excluir(id_jog):
    jogadores = session.get('jogadores', [])
    # Filtra mantendo todos, exceto o que tem o ID selecionado
    session['jogadores'] = [j for j in jogadores if j['id'] != id_jog]
    session.modified = True
    return redirect('/')

@app.route('/excluir_todos')
def excluir_todos():
    session['jogadores'] = []
    session.modified = True
    flash("Lista de jogadores limpa com sucesso!", "sucesso")
    return redirect('/')

@app.route('/sortear', methods=['POST'])
def sortear():
    num_times = int(request.form.get('num_times', 2))
    tamanho_time = int(request.form.get('tamanho_time', 5))
    jogadores = session.get('jogadores', [])
    
    times, erro = realizar_sorteio(num_times, tamanho_time, jogadores)
    
    if erro:
        flash(erro, 'erro')
        return redirect('/')
        
    return render_template('index.html', jogadores=jogadores, niveis=NIVEIS_NOME, times=times)

if __name__ == '__main__':
    app.run(debug=True)