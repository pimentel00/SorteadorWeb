from flask import Flask, render_template, request, redirect, flash
import random

app = Flask(__name__)
app.secret_key = 'chave_secreta_sorteador' 

jogadores = []
ID_CONTADOR = 0

NIVEIS_NOME = {
    1: "Ruim",
    2: "Decente",
    3: "Técnico",
    4: "Veloz"
}

def realizar_sorteio(num_times, tamanho_time):
    total_necessario = num_times * tamanho_time
    
    if len(jogadores) < total_necessario:
        return None, f"ERRO: Faltam {total_necessario - len(jogadores)} jogadores para o sorteio."

    # Define os pesos de força de cada nível
    pesos = {
        3: 40, # Técnico (O mais importante)
        4: 30, # Veloz (Segundo mais importante)
        2: 20, # Decente
        1: 10  # Ruim
    }

    # Embaralha todos os jogadores primeiro para garantir aleatoriedade entre pessoas do mesmo nível
    jogadores_misturados = list(jogadores)
    random.shuffle(jogadores_misturados)

    # Ordena a lista do jogador mais "pesado" para o mais "leve"
    jogadores_ordenados = sorted(jogadores_misturados, key=lambda j: pesos[j['nivel']], reverse=True)

    # Cria a estrutura dos times, agora guardando a lista de jogadores e os pontos totais do time
    times_info = [{'jogadores': [], 'pontos': 0} for _ in range(num_times)]

    # Distribui os jogadores
    for jogador in jogadores_ordenados:
        peso_jogador = pesos[jogador['nivel']]
        
        # Filtra apenas os times que ainda têm vaga
        times_com_vaga = [t for t in times_info if len(t['jogadores']) < tamanho_time]
        if not times_com_vaga:
            break
            
        # A MÁGICA: Ordena os times disponíveis pela pontuação atual (do menor para o maior).
        # Se houver empate na pontuação, desempatamos pelo time com menos jogadores.
        times_com_vaga.sort(key=lambda t: (t['pontos'], len(t['jogadores'])))
        
        # O time mais "fraco" no momento recebe o próximo melhor jogador disponível
        time_escolhido = times_com_vaga[0]
        time_escolhido['jogadores'].append(jogador)
        time_escolhido['pontos'] += peso_jogador

    return times_info, None

@app.route('/')
def index():
    return render_template('index.html', jogadores=jogadores, niveis=NIVEIS_NOME)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    global ID_CONTADOR
    nome = request.form.get('nome').strip().title()
    nivel = int(request.form.get('nivel'))
    if nome:
        jogadores.append({'id': ID_CONTADOR, 'nome': nome, 'nivel': nivel})
        ID_CONTADOR += 1
    return redirect('/')

@app.route('/excluir/<int:id_jog>')
def excluir(id_jog):
    global jogadores
    jogador = next((j for j in jogadores if j['id'] == id_jog), None)
    if jogador: jogadores.remove(jogador)
    return redirect('/')

@app.route('/excluir_todos')
def excluir_todos():
    global jogadores, ID_CONTADOR
    jogadores = []
    ID_CONTADOR = 0
    flash("Lista de jogadores limpa com sucesso!", "sucesso")
    return redirect('/')

@app.route('/sortear', methods=['POST'])
def sortear():
    num_times = int(request.form.get('num_times', 2))
    tamanho_time = int(request.form.get('tamanho_time', 5))
    times, erro = realizar_sorteio(num_times, tamanho_time)
    if erro:
        flash(erro, 'erro')
        return redirect('/')
    return render_template('index.html', jogadores=jogadores, niveis=NIVEIS_NOME, times=times)

if __name__ == '__main__':
    app.run(debug=True)