from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
import secrets
import requests

app = Flask(__name__)

# Configuração do Mailgun
MAILGUN_API_KEY = "sua_api_key_aqui"  # Substitua pela sua chave do Mailgun
MAILGUN_DOMAIN = "sandbox<seu_dominio>.mailgun.org"  # Substitua pelo seu domínio sandbox
FROM_EMAIL = f"no-reply@{MAILGUN_DOMAIN}"

# Lista de usuários confirmados
users = [
    {'id': 1, 'username': 'superadmin', 'password': 'super123', 'role': 'superadmin', 'email': 'superadmin@example.com'},
    {'id': 2, 'username': 'workspacemanager', 'password': 'work123', 'role': 'workspace_manager', 'email': 'work@example.com'},
    {'id': 3, 'username': 'teammanager', 'password': 'team123', 'role': 'team_manager', 'email': 'team@example.com'},
    {'id': 4, 'username': 'taskcreator', 'password': 'task123', 'role': 'task_creator', 'email': 'task@example.com'}
]

# Lista de usuários pendentes (antes da ativação)
pending_users = {}

# Lista de workspaces
workspaces = [
    {
        'id': 1,
        'name': 'Projeto Marketing',
        'teams': [
            {'id': 1, 'name': 'Equipe A', 'members': ['Alice', 'Bob']},
            {'id': 2, 'name': 'Equipe B', 'members': ['Charlie', 'Diana']}
        ]
    },
    {
        'id': 2,
        'name': 'Desenvolvimento',
        'teams': [
            {'id': 3, 'name': 'Equipe Dev', 'members': ['Eve', 'Frank']}
        ]
    },
    {
        'id': 3,
        'name': 'Teste Geral',
        'teams': [
            {'id': 4, 'name': 'Equipe Teste 1', 'members': ['João', 'Maria']},
            {'id': 5, 'name': 'Equipe Teste 2', 'members': ['Pedro', 'Ana']}
        ]
    }
]

# Lista de tarefas
tasks = [
    {
        'id': 1,
        'title': 'Criar apresentação',
        'description': 'Preparar slides para reunião',
        'status': 'Para Fazer',
        'priority': 'Média',
        'start_date': '2025-04-01',
        'due_date': '2025-04-05',
        'assigned_to': 'João',
        'workspace_id': 3,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'id': 2,
        'title': 'Revisar código',
        'description': 'Checar bugs no sistema',
        'status': 'Em Atraso',
        'priority': 'Alta',
        'start_date': '2025-03-30',
        'due_date': '2025-04-02',
        'assigned_to': 'Maria',
        'workspace_id': 3,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
]

# Função para verificar permissões
def check_permission(user_id, allowed_roles):
    user = next((u for u in users if u['id'] == user_id), None)
    if not user or user['role'] not in allowed_roles:
        return False
    return True

def send_activation_email(email, token):
    activation_link = f"http://127.0.0.1:5000/activate/{token}"
    subject = "Confirme seu cadastro"
    body = f"Olá! Clique no link para confirmar seu cadastro: {activation_link}"

    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": FROM_EMAIL,
                "to": email,
                "subject": subject,
                "text": body
            }
        )
        if response.status_code == 200:
            print(f"E-mail de ativação enviado para {email}")
        else:
            print(f"Erro ao enviar e-mail: {response.text}")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {str(e)}")

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Nenhum dado enviado'}), 400
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        if not username or not password or not email:
            return jsonify({'error': 'Usuário, senha e e-mail são obrigatórios'}), 400
        
        # Verifica se o username ou email já existe
        if any(u['username'] == username or u['email'] == email for u in users):
            return jsonify({'error': 'Usuário ou e-mail já cadastrado'}), 400
        
        # Gera um token único para ativação
        token = secrets.token_urlsafe(16)
        pending_users[token] = {
            'id': len(users) + len(pending_users) + 1,
            'username': username,
            'password': password,
            'email': email,
            'role': 'task_creator'  # Novo usuário começa como task_creator
        }
        
        # Envia o e-mail de ativação
        send_activation_email(email, token)
        return jsonify({'message': 'Cadastro realizado! Verifique seu e-mail para confirmar.'}), 201
    except Exception as e:
        print(f"Erro no registro: {str(e)}")
        return jsonify({'error': 'Erro interno no servidor'}), 500

@app.route('/activate/<token>', methods=['GET'])
def activate(token):
    if token in pending_users:
        user = pending_users.pop(token)
        users.append(user)
        return jsonify({'message': f"Conta ativada com sucesso! Bem-vindo, {user['username']}."}), 200
    return jsonify({'error': 'Token inválido ou expirado'}), 400

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Nenhum dado enviado'}), 400
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({'error': 'Usuário e senha são obrigatórios'}), 400
        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        if user:
            return jsonify({'message': 'Login bem-sucedido!', 'user_id': user['id'], 'role': user['role']}), 200
        return jsonify({'error': 'Credenciais inválidas'}), 401
    except Exception as e:
        print(f"Erro no login: {str(e)}")
        return jsonify({'error': 'Erro interno no servidor'}), 500

@app.route('/workspaces', methods=['GET'])
def get_workspaces():
    return jsonify(workspaces)

@app.route('/workspaces', methods=['POST'])
def create_workspace():
    user_id = request.headers.get('User-ID', type=int)
    if not check_permission(user_id, ['superadmin', 'workspace_manager']):
        return jsonify({'error': 'Permissão negada'}), 403
    data = request.get_json()
    name = data.get('name')
    if name:
        workspace = {
            'id': len(workspaces) + 1,
            'name': name,
            'teams': []
        }
        workspaces.append(workspace)
        return jsonify({'message': 'Workspace criado com sucesso!', 'workspace': workspace}), 201
    return jsonify({'error': 'Nome é obrigatório'}), 400

@app.route('/workspaces/<int:workspace_id>', methods=['PUT'])
def update_workspace(workspace_id):
    user_id = request.headers.get('User-ID', type=int)
    if not check_permission(user_id, ['superadmin']):
        return jsonify({'error': 'Permissão negada'}), 403
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Nome é obrigatório'}), 400
    for workspace in workspaces:
        if workspace['id'] == workspace_id:
            workspace['name'] = name
            return jsonify({'message': 'Workspace atualizado com sucesso!', 'workspace': workspace}), 200
    return jsonify({'error': 'Workspace não encontrado'}), 404

@app.route('/workspaces/<int:workspace_id>', methods=['DELETE'])
def delete_workspace(workspace_id):
    user_id = request.headers.get('User-ID', type=int)
    if not check_permission(user_id, ['superadmin']):
        return jsonify({'error': 'Permissão negada'}), 403
    for i, workspace in enumerate(workspaces):
        if workspace['id'] == workspace_id:
            global tasks
            tasks = [task for task in tasks if task['workspace_id'] != workspace_id]
            del workspaces[i]
            return jsonify({'message': 'Workspace excluído com sucesso!'}), 200
    return jsonify({'error': 'Workspace não encontrado'}), 404

@app.route('/teams', methods=['POST'])
def create_team():
    user_id = request.headers.get('User-ID', type=int)
    if not check_permission(user_id, ['superadmin', 'workspace_manager', 'team_manager']):
        return jsonify({'error': 'Permissão negada'}), 403
    data = request.get_json()
    name = data.get('name')
    members = data.get('members', [])
    workspace_id = data.get('workspace_id')
    if name and workspace_id:
        for workspace in workspaces:
            if workspace['id'] == workspace_id:
                team = {
                    'id': len([t for w in workspaces for t in w['teams']]) + 1,
                    'name': name,
                    'members': members
                }
                workspace['teams'].append(team)
                return jsonify({'message': 'Equipe criada com sucesso!'}), 201
    return jsonify({'error': 'Nome e workspace_id são obrigatórios'}), 400

@app.route('/teams/<int:team_id>', methods=['PUT'])
def update_team(team_id):
    user_id = request.headers.get('User-ID', type=int)
    if not check_permission(user_id, ['superadmin']):
        return jsonify({'error': 'Permissão negada'}), 403
    data = request.get_json()
    new_members = data.get('members', [])
    for workspace in workspaces:
        for team in workspace['teams']:
            if team['id'] == team_id:
                team['members'] = new_members
                return jsonify({'message': 'Equipe atualizada com sucesso!'}), 200
    return jsonify({'error': 'Equipe não encontrada'}), 404

@app.route('/teams/<int:team_id>/members', methods=['POST'])
def add_team_members(team_id):
    user_id = request.headers.get('User-ID', type=int)
    if not check_permission(user_id, ['superadmin', 'workspace_manager', 'team_manager']):
        return jsonify({'error': 'Permissão negada'}), 403
    data = request.get_json()
    new_members = data.get('members', [])
    for workspace in workspaces:
        for team in workspace['teams']:
            if team['id'] == team_id:
                current_members = set(team['members'])
                new_unique_members = [m for m in new_members if m not in current_members]
                team['members'].extend(new_unique_members)
                return jsonify({'message': 'Membros adicionados com sucesso!', 'added': new_unique_members}), 200
    return jsonify({'error': 'Equipe não encontrada'}), 404

@app.route('/teams/<int:team_id>/members', methods=['DELETE'])
def remove_team_members(team_id):
    user_id = request.headers.get('User-ID', type=int)
    if not check_permission(user_id, ['superadmin', 'workspace_manager', 'team_manager']):
        return jsonify({'error': 'Permissão negada'}), 403
    data = request.get_json()
    members_to_remove = data.get('members', [])
    for workspace in workspaces:
        for team in workspace['teams']:
            if team['id'] == team_id:
                team['members'] = [m for m in team['members'] if m not in members_to_remove]
                return jsonify({'message': 'Membros removidos com sucesso!', 'removed': members_to_remove}), 200
    return jsonify({'error': 'Equipe não encontrada'}), 404

@app.route('/tasks', methods=['GET'])
def get_tasks():
    workspace_id = request.args.get('workspace_id', type=int)
    if workspace_id:
        return jsonify([task for task in tasks if task['workspace_id'] == workspace_id])
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def add_task():
    user_id = request.headers.get('User-ID', type=int)
    if not check_permission(user_id, ['superadmin', 'workspace_manager', 'team_manager', 'task_creator']):
        return jsonify({'error': 'Permissão negada'}), 403
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')
    status = data.get('status', 'Para Fazer')
    priority = data.get('priority', 'Média')
    start_date = data.get('start_date')
    due_date = data.get('due_date')
    assigned_to = data.get('assigned_to', None)
    workspace_id = data.get('workspace_id')
    if title and workspace_id:
        task = {
            'id': len(tasks) + 1,
            'title': title,
            'description': description,
            'status': status,
            'priority': priority,
            'start_date': start_date,
            'due_date': due_date,
            'assigned_to': assigned_to,
            'workspace_id': workspace_id,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        tasks.append(task)
        return jsonify({'message': 'Tarefa adicionada com sucesso!'}), 201
    return jsonify({'error': 'Título e workspace são obrigatórios'}), 400

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    user_id = request.headers.get('User-ID', type=int)
    if not check_permission(user_id, ['superadmin']):
        return jsonify({'error': 'Permissão negada'}), 403
    data = request.get_json()
    for task in tasks:
        if task['id'] == task_id:
            task['status'] = data.get('status', task['status'])
            task['priority'] = data.get('priority', task['priority'])
            task['start_date'] = data.get('start_date', task['start_date'])
            task['due_date'] = data.get('due_date', task['due_date'])
            task['assigned_to'] = data.get('assigned_to', task['assigned_to'])
            return jsonify({'message': 'Tarefa atualizada!'}), 200
    return jsonify({'error': 'Tarefa não encontrada'}), 404

if __name__ == '__main__':
    app.run(debug=True)
else:
    # Necessário para Vercel
    from wsgi import app as application