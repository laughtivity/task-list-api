from flask import Blueprint, jsonify, request, abort, make_response
from app import db
from app.models.task import Task

# BLUEPRINTS
task_bp = Blueprint("tasks", __name__, url_prefix = "/tasks")

# HELPER FUNCTIONS
def validate_model(cls, model_id):
    # makes sure the data type is an integer
    try: 
        model_id = int(model_id)
    except ValueError:
        abort(make_response({"message": f"{model_id} is not a valid type. A {(type(model_id))} data type was provided. Must be a valid integer data type."},400))
    
    # model_id is confirmed an integer so connect with db
    # changed Crystal to cls to utilize
    model = cls.query.get(model_id)

    if not model:
        abort(make_response({"message:" : f"{cls.__name__} {model_id} does not exist"},404))
    
    return model
# POST METHOD - create a task 
# - complete_at defaults with null
# RETURN - 201 CREATED // task: id / title/ description / is complete
@task_bp.route("", methods = ["POST"])
def create_task():
    request_body = request.get_json()

    new_task = Task.from_dict(request_body)

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

    tasks = Task.query.all()

    for task in tasks:
        tasks_response.append(task.to_dict())
    
    return jsonify(tasks_response)


# GET METHOD - read a task by task id
# RETURN - 200 OK, task : id / title / description / is complete
@task_bp.route("/<task_id>", methods = ["GET"])
def read_by_task_id(task_id):
    task = validate_model(Task, task_id)

    return task.to_dict(), 200


# PUT METHOD - update a task by id
# - update title
# - update description
# RETURN - 