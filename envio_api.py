import requests
import psycopg2  # Biblioteca para PostgreSQL

# Configuração da API
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxMzIiLCJqdGkiOiI1MTNhMDdhMDdmMmY4OTI5MWUyMzQ5MTVmMDY5ODIyYWZhNjkxZDAwZGQ2YzZiNjVkM2IyMmY1N2QwNzNmZTEzN2NhMjMxZDc1MmQwMTg3YSIsImlhdCI6MTczNzA1Mjk4Ny40MTIwNDgsIm5iZiI6MTczNzA1Mjk4Ny40MTIwNTIsImV4cCI6MTg5NDgxOTM4Ny40MDM0MDcsInN1YiI6IjMxOSIsInNjb3BlcyI6WyIqIl19.UP9ThFiYOvtjr2JOQuu0nSWzroOz6WmWCnfNK4yhU-j_02pcDT1hukXrgV_FnsCqy37kGgAZVXT-uk2TLr8RWxMww4JXtqLDCdH6uSmQvO2uK1HAutxkoJNFDurIjTcfX2RmbQ4_TD0QUc2pyyHZ9lB9C4nOlOvRLkJIOoyGAa3gUlTHgX8GN5x2ZS_2bxrYPy4ioFDMNTwCi5UG_fXbApmVuXvhc35muacC1TVmuExvGQLpliDsZqNNJgZSVZsqdhFQS4ZrqYMz-pkd0_W0AuCSYxjMKyEAjcd6aEQfkLiGfVzI0EJ19e1Yc-vBG1SxC4Iv7FfhL6H9hahMZ-sQK07Ilbt9vD7k-I-93vvHBmlYIT4A4wC9QqH-z-I0hg64JjYsPLBezqmZOUEmcsan30OFZSlSp2iRkgd4iEnvia41KdkllERkoPPu5o4fq8hQ6dfVvGsqSQ0ZdMRWy0ukWTdAvgExFCh3i7Q6hadvdePrSzNUIrESp4tKpTg5qtVtbaseZNz7IkzpuYbk8tJUolNIterF20nc0leBbk2Qx0cjrrw6Cyzu7AElUxG-vALI5FRmR9jsWT_knrSQaWZaRo1tHrCF0yG19odOjS8Scd-97JTzN-gStji6XyDl5fTQV0uljHS3CqyTFDcWl9ZRk3wI5ITjFgYaiVEIkZ7U5p4"
HEADERS = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

# Configuração do banco de dados PostgreSQL
db_config = {
    "dbname": "BOLETOS",
    "user": "postgres",
    "password": "teste",
    "host": "192.168.1.163",
    "port": "5432"
}

# 🔹 Mapeamento manual de unidades e IDs
unidades_api = {
    "Bento Ribeiro": 35022,
    "Madureira": 35023,
    "Santa Cruz": 35024,
    "Cascadura": 35025,
    "Taquara": 35026,
    "Nilopolis": 35027,
    "Seropédica": 35028,
    "Barra da Tijuca": 35029,
    "Campo Grande": 35030,
    "Maricá": 35031,
    "Ilha do Governador": 35032,
    "Freguesia": 35033,
    "Recreio dos Bandeirantes": 35034
}

# Obter turmas da API
def obter_turmas_api(unit_id, nome_turma):
    url = "https://app.redacaonline.com.br/api/classes"
    payload = {"name": nome_turma, "unit_id": unit_id}
    response = requests.get(url, headers=HEADERS, params=payload)

    try:
        turmas = response.json()  # A resposta é uma lista de dicionários
        if not isinstance(turmas, list):  # Caso a resposta não seja uma lista, tratamos o erro
            print(f"⚠ Resposta inesperada da API: {turmas}")
            return None

        # Buscar a turma correta pelo nome
        for turma in turmas:
            if turma["name"] == str(nome_turma):
                return turma["id"]

        print(f"⚠ Turma '{nome_turma}' não encontrada na unidade {unit_id}.")
        return None

    except Exception as e:
        print(f"Erro ao obter turmas: {e}")
        return None

# Buscar alunos paginados
def listar_alunos():
    url = "https://app.redacaonline.com.br/api/students"
    alunos = []
    page = 1

    while True:
        print(f"🔄 Buscando alunos na página {page}...")  # Log de progresso
        response = requests.get(url, headers=HEADERS, params={"page": page}, timeout=10)
        
        if response.status_code != 200:
            print(f"Erro ao listar alunos: {response.text}")
            return []
        
        data = response.json()
        alunos.extend(data.get("data", []))
        
        if "next_page_url" not in data or not data["next_page_url"]:
            print("✅ Todas as páginas de alunos foram carregadas.")
            break
        
        page += 1
    
    return alunos

# Obter aluno na API pelo external_id
def obter_aluno_api(matricula):
    alunos = listar_alunos()
    for aluno in alunos:
        if aluno["external_id"] == str(matricula):
            return aluno
    return None

# Obter student_id pelo nome do aluno
def obter_student_id(nome_aluno):
    alunos = listar_alunos()
    for aluno in alunos:
        if aluno["name"].lower() == nome_aluno.lower():
            return aluno["id"]
    print(f"Aluno '{nome_aluno}' não encontrado.")
    return None

# Remover aluno
def remover_aluno(nome_aluno):
    student_id = obter_student_id(nome_aluno)
    if not student_id:
        print("Não foi possível encontrar o aluno.")
        return

    url = f"https://app.redacaonline.com.br/api/students/{student_id}"
    response = requests.delete(url, headers=HEADERS)

    if response.status_code == 204:
        print(f"Aluno {nome_aluno} removido com sucesso!")
    else:
        print(f"Erro ao remover aluno: {response.status_code} - {response.text}")

# Atualizar aluno na API
def atualizar_aluno(student_id, nome, email, class_id, external_id):
    url = f"https://app.redacaonline.com.br/api/students/{student_id}"
    payload = {
        "name": nome,
        "email": email,
        "class_id": class_id,
        "external_id": str(external_id)
    }
    response = requests.put(url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        print(f"Aluno {nome} atualizado com sucesso!")
    else:
        print(f"Erro ao atualizar aluno: {response.status_code} - {response.text}")

# Inserir aluno na API
def inserir_aluno(nome, matricula, class_id):
    url = "https://app.redacaonline.com.br/api/students"
    email = f"{matricula}@alunos.smrede.com.br"
    payload = {"name": nome, "email": email, "class_id": class_id, "external_id": str(matricula)}
    response = requests.post(url, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        aluno_data = response.json()
        aluno_id = aluno_data.get("id", "ID não encontrado")
        print(f"Aluno {nome} inserido com sucesso! ID: {aluno_id}")
    elif response.status_code == 400:
        print(f"Erro ao inserir aluno: {response.text}")
    else:
        print(f"Erro inesperado: {response.status_code} - {response.text}")

# Mapeamento de código -> nome da unidade
codigo_para_unidade = {
    "01": "Bento Ribeiro",
    "02": "Madureira",
    "03": "Santa Cruz",
    "04": "Cascadura",
    "05": "Taquara",
    "06": "Nilopolis",
    "09": "Seropédica",
    "10": "Barra da Tijuca",
    "11": "Campo Grande",
    "14": "Maricá",
    "15": "Ilha do Governador",
    "16": "Freguesia",
    "17": "Recreio dos Bandeirantes"
}

def processar_alunos():
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(""" 
        SELECT unidade, sit, matricula, nome, turma 
        FROM alunos_25_geral 
        WHERE turma::NUMERIC >= 11900::NUMERIC
    """)
    
    alunos = cursor.fetchall()
    conn.close()
    
    alunos_api = listar_alunos()  # 🔹 Obtém a lista de alunos apenas uma vez
    alteracoes_feitas = False

    for unidade_codigo, sit, matricula, nome, turma in alunos:
        unidade_codigo = unidade_codigo.strip().zfill(2)
        unidade_nome = codigo_para_unidade.get(unidade_codigo)
        
        if not unidade_nome:
            print(f"⚠ Unidade com código '{unidade_codigo}' não encontrada no mapeamento.")
            continue

        unit_id = unidades_api.get(unidade_nome)

        if not unit_id:
            print(f"⚠ Unidade '{unidade_nome}' não encontrada no dicionário de IDs.")
            continue

        class_id = obter_turmas_api(unit_id, turma)
        if not class_id:
            print(f"⚠ Turma {turma} não encontrada para a unidade {unidade_nome}.")
            continue

        # 🔹 Busca o aluno na lista já carregada
        aluno_api = next((aluno for aluno in alunos_api if aluno["external_id"] == str(matricula)), None)

        if sit in [2, 4] and aluno_api:
            remover_aluno(aluno_api["name"])
            alteracoes_feitas = True
        elif not aluno_api:
            inserir_aluno(nome, matricula, class_id)
            alteracoes_feitas = True
        elif aluno_api["class_id"] != class_id or aluno_api["name"] != nome:
            atualizar_aluno(aluno_api["id"], nome, aluno_api["email"], class_id, matricula)
            alteracoes_feitas = True

    if not alteracoes_feitas:
        print(f"✅ Todos os alunos da unidade {unidade_codigo} já estão corretos na API. Nenhuma alteração necessária.")
    else:
        print(f"🔄 Alterações concluídas na base de dados da unidade {unidade_codigo}.")

# Executar
if __name__ == "__main__":
    processar_alunos()