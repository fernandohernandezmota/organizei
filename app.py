from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime

app = Flask(__name__)

# Lista de workspaces
workspaces = [
    {
        "id": 1,
        "name": "Projeto Marketing",
        "teams": [
            {"id": 1, "name": "Equipe A", "members": ["Alice", "Bob"]},
            {"id": 2, "name": "Equipe B", "members": ["Charlie", "Diana"]},
        ],
    },
    {
        "id": 2,
        "name": "Desenvolvimento",
        "teams": [{"id": 3, "name": "Equipe Dev", "members": ["Eve", "Frank"]}],
    },
    {
        "id": 3,
        "name": "Teste Geral",
        "teams": [
            {"id": 4, "name": "Equipe Teste 1", "members": ["João", "Maria"]},
            {"id": 5, "name": "Equipe Teste 2", "members": ["Pedro", "Ana"]},
        ],
    },
]

# Lista de tarefas com os novos campos: priority, start_date, due_date
tasks = [
    {
        "id": 1,
        "title": "Criar apresentação",
        "description": "Preparar slides para reunião",
        "status": "Para Fazer",
        "priority": "Média",
        "start_date": "2025-04-01",
        "due_date": "2025-04-05",
        "assigned_to": "João",
        "workspace_id": 3,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
    {
        "id": 2,
        "title": "Revisar código",
        "description": "Checar bugs no sistema",
        "status": "Em Atraso",
        "priority": "Alta",
        "start_date": "2025-03-30",
        "due_date": "2025-04-02",
        "assigned_to": "Maria",
        "workspace_id": 3,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
    {
        "id": 3,
        "title": "Enviar relatório",
        "description": "Finalizar e enviar relatório mensal",
        "status": "Concluído",
        "priority": "Baixa",
        "start_date": "2025-03-25",
        "due_date": "2025-03-31",
        "assigned_to": "Pedro",
        "workspace_id": 3,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
    {
        "id": 4,
        "title": "Reunião de planejamento",
        "description": "Definir metas do mês",
        "status": "Pendente",
        "priority": "Média",
        "start_date": "2025-04-02",
        "due_date": "2025-04-03",
        "assigned_to": "Ana",
        "workspace_id": 3,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
    {
        "id": 5,
        "title": "Aguardar feedback",
        "description": "Esperar retorno do cliente",
        "status": "Aguardando",
        "priority": "Baixa",
        "start_date": "2025-04-01",
        "due_date": "2025-04-07",
        "assigned_to": None,
        "workspace_id": 3,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
    {
        "id": 6,
        "title": "Revisão final",
        "description": "Revisar documento antes da entrega",
        "status": "Aprovação",
        "priority": "Alta",
        "start_date": "2025-04-03",
        "due_date": "2025-04-04",
        "assigned_to": "João",
        "workspace_id": 3,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
    {
        "id": 7,
        "title": "Publicar site",
        "description": "Lançar nova versão do site",
        "status": "Aprovado",
        "priority": "Média",
        "start_date": "2025-03-28",
        "due_date": "2025-04-01",
        "assigned_to": "Maria",
        "workspace_id": 3,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
]


@app.route("/")
def serve_index():
    return send_from_directory("static", "index.html")


@app.route("/workspaces", methods=["GET"])
def get_workspaces():
    return jsonify(workspaces)


@app.route("/workspaces", methods=["POST"])
def create_workspace():
    data = request.get_json()
    name = data.get("name")
    if name:
        workspace = {"id": len(workspaces) + 1, "name": name, "teams": []}
        workspaces.append(workspace)
        return (
            jsonify(
                {"message": "Workspace criado com sucesso!", "workspace": workspace}
            ),
            201,
        )
    return jsonify({"error": "Nome é obrigatório"}), 400


@app.route("/teams", methods=["POST"])
def create_team():
    data = request.get_json()
    name = data.get("name")
    members = data.get("members", [])
    workspace_id = data.get("workspace_id")
    if name and workspace_id:
        for workspace in workspaces:
            if workspace["id"] == workspace_id:
                team = {
                    "id": len([t for w in workspaces for t in w["teams"]]) + 1,
                    "name": name,
                    "members": members,
                }
                workspace["teams"].append(team)
                return jsonify({"message": "Equipe criada com sucesso!"}), 201
    return jsonify({"error": "Nome e workspace_id são obrigatórios"}), 400


@app.route("/teams/<int:team_id>", methods=["PUT"])
def update_team(team_id):
    data = request.get_json()
    new_members = data.get("members", [])
    for workspace in workspaces:
        for team in workspace["teams"]:
            if team["id"] == team_id:
                team["members"] = new_members
                return jsonify({"message": "Equipe atualizada com sucesso!"}), 200
    return jsonify({"error": "Equipe não encontrada"}), 404


@app.route("/teams/<int:team_id>/members", methods=["POST"])
def add_team_members(team_id):
    data = request.get_json()
    new_members = data.get("members", [])
    for workspace in workspaces:
        for team in workspace["teams"]:
            if team["id"] == team_id:
                current_members = set(team["members"])
                new_unique_members = [
                    m for m in new_members if m not in current_members
                ]
                team["members"].extend(new_unique_members)
                return (
                    jsonify(
                        {
                            "message": "Membros adicionados com sucesso!",
                            "added": new_unique_members,
                        }
                    ),
                    200,
                )
    return jsonify({"error": "Equipe não encontrada"}), 404


@app.route("/teams/<int:team_id>/members", methods=["DELETE"])
def remove_team_members(team_id):
    data = request.get_json()
    members_to_remove = data.get("members", [])
    for workspace in workspaces:
        for team in workspace["teams"]:
            if team["id"] == team_id:
                team["members"] = [
                    m for m in team["members"] if m not in members_to_remove
                ]
                return (
                    jsonify(
                        {
                            "message": "Membros removidos com sucesso!",
                            "removed": members_to_remove,
                        }
                    ),
                    200,
                )
    return jsonify({"error": "Equipe não encontrada"}), 404


@app.route("/tasks", methods=["GET"])
def get_tasks():
    workspace_id = request.args.get("workspace_id", type=int)
    if workspace_id:
        return jsonify([task for task in tasks if task["workspace_id"] == workspace_id])
    return jsonify(tasks)


@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description", "")
    status = data.get("status", "Para Fazer")
    priority = data.get("priority", "Média")  # Prioridade padrão
    start_date = data.get("start_date")
    due_date = data.get("due_date")
    assigned_to = data.get("assigned_to", None)
    workspace_id = data.get("workspace_id")
    if title and workspace_id:
        task = {
            "id": len(tasks) + 1,
            "title": title,
            "description": description,
            "status": status,
            "priority": priority,
            "start_date": start_date,
            "due_date": due_date,
            "assigned_to": assigned_to,
            "workspace_id": workspace_id,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        tasks.append(task)
        return jsonify({"message": "Tarefa adicionada com sucesso!"}), 201
    return jsonify({"error": "Título e workspace são obrigatórios"}), 400


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = data.get("status", task["status"])
            task["priority"] = data.get("priority", task["priority"])
            task["start_date"] = data.get("start_date", task["start_date"])
            task["due_date"] = data.get("due_date", task["due_date"])
            task["assigned_to"] = data.get("assigned_to", task["assigned_to"])
            return jsonify({"message": "Tarefa atualizada!"}), 200
    return jsonify({"error": "Tarefa não encontrada"}), 404


if __name__ == "__main__":
    app.run(debug=True)
