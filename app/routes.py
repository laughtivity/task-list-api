from flask import Blueprint, jsonify, request, abort, make_response
from app import db
from app.models.task import Task

task_bp = Blueprint("tasks", __name__, url_prefix = "/tasks")

# POST METHOD - create a task 
# - complete_at defaults with null
# RETURN - 201 CREATED // task: id / title/ description / is complete
@task_bp.route("", methods = ["POST"])
def create_task():
    request_body = request.get_json()

    new_task = Task(
        title = request_body["title"],
        description = request_body["description"],
        completed_at = request_body["completed_at"]
    )

    db.session.add(new_task)
    db.session.commit()

    return jsonify({
        "task": {
            "id": new_task.task_id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": new_task.is_complete

        }, 
    }), 201

# GET METHOD - read all task
# - id / title / description / is_complete
# RETURN - 200 OK, empty list if no saved tasks
# RETURN - 200 OK, list w/ id / title / description / is complete 
@task_bp.route("", methods = ["GET"])
def read_all_tasks():
    tasks_response = []

    

# GET METHOD - read a task by task id
# RETURN - 200 OK, task : id / title / description / is complete

# PUT METHOD - update a task by id
# - update title
# - update description
# RETURN - 