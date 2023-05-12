from flask import Blueprint, jsonify, request, abort, make_response
from app import db
from app.models.task import Task
from app.models.goal import Goal
from datetime import datetime
import requests

# BLUEPRINTS #
task_bp = Blueprint("tasks", __name__, url_prefix = "/tasks")
goal_bp = Blueprint("goals", __name__, url_prefix = "/goals")

# HELPER FUNCTIONS #
def validate_model(cls, model_id):
    try: 
        model_id = int(model_id)
    except ValueError:
        abort(make_response({"message": f"{model_id} is not a valid type. A {(type(model_id))} data type was provided. Must be a valid integer data type."},400))
    
    model = cls.query.get(model_id)
    if not model:
        abort(make_response({"message" : f"{cls.__name__} {model_id} does not exist"},404))
    
    return model

def slack_bot_notification(task):
# SLACK IMPLEMENTATION USING HTTP REQUESTS
# https://stackoverflow.com/questions/63899742/how-to-use-mock-in-request-post-to-an-external-api
    import os

    api_url = "https://slack.com/api/chat.postMessage"
    slack_token = os.environ.get("SLACK_WEB_API_KEY")
    headers = {"Authorization": slack_token}
    body = {
        "channel": "task-notifications",
        "text": f"Someone just completed the task {task.title}" 
        }
    response = requests.post(api_url, headers=headers, params=body)


# POST METHOD - create task
@task_bp.route("", methods = ["POST"])
def create_task():
    request_body = request.get_json()
    try:
        new_task = Task.from_dict(request_body)
    except:
        return jsonify({"details": "Invalid data"}),400
    
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"task": new_task.to_dict()}), 201

# GET METHOD - read all task
@task_bp.route("", methods = ["GET"])
def get_all_tasks():
    tasks_response = []
    tasks = Task.query.all()

    # for task in tasks:
    #     tasks_response.append(task.to_dict())
    tasks_response = [task.to_dict() for task in tasks]

    # https://www.programiz.com/python-programming/methods/list/sort
    # sort by asc/desc
    sort_query = request.args.get("sort")
    if sort_query == "asc":
        tasks_response.sort(key=lambda x: x.get('title'))
    elif sort_query == "desc":
        tasks_response.sort(key=lambda x: x.get('title'), reverse=True)
    # tasks_response = check_sort(tasks_response)

    return jsonify(tasks_response)

# GET METHOD - read a task by task id
@task_bp.route("/<task_id>", methods = ["GET"])
def get_by_task_id(task_id):
    task = validate_model(Task, task_id)
    return {"task": task.to_dict()}, 200

# PUT METHOD - update a task by id
@task_bp.route("/<task_id>", methods = ["PUT"])
def update_task(task_id):
    task = validate_model(Task,task_id)
    request_body = request.get_json()

    try:
        task.title = request_body["title"]
        task.description = request_body["description"]
    except:
        return jsonify({"details": "Missing data"}),400

    db.session.commit()
    return jsonify({"task": task.to_dict()}), 200

# DELETE METHOD - delete a task by id
@task_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = validate_model(Task, task_id)

    db.session.delete(task)
    db.session.commit()

    return {"details": f'Task {task_id} "{task.title}" successfully deleted'}



# PUT METHOD - update is_complete to true
@task_bp.route("/<task_id>/mark_complete", methods = ["PATCH"])
def mark_complete(task_id):
    task = validate_model(Task, task_id)

    task.is_complete = True
    task.completed_at = datetime.utcnow()

    db.session.commit()
    slack_bot_notification(task)
    return {"task": task.to_dict()}, 200

# PUT METHOD - update is_complete to false
@task_bp.route("/<task_id>/mark_incomplete", methods = ["PATCH"])
def mark_incomplete(task_id):
    task = validate_model(Task, task_id)

    task.is_complete = False
    task.completed_at = None

    db.session.commit()
    return {"task": task.to_dict()}, 200



# POST METHOD - create a goal
@goal_bp.route("", methods=["POST"])
def create_goal():
    request_body = request.get_json()

    try:
        new_goal = Goal.from_dict(request_body)
    except:
        return jsonify({"details": "Invalid data"}), 400
    
    db.session.add(new_goal)
    db.session.commit()
    return jsonify({"goal": new_goal.to_dict()}), 201

# GET METHOD - get all goals
@goal_bp.route("", methods=["GET"])
def get_all_goals():
    goals_response = []
    goals = Goal.query.all()

    # for goal in goals:
    #     goals_response.append(goal.to_dict())
    goals_response = [goal.to_dict() for goal in goals]
    # goals_response = check_sort(goals_response)
    
    # # https://www.programiz.com/python-programming/methods/list/sort
    sort_query = request.args.get("sort")
    if sort_query == "asc":
        goals_response.sort(key=lambda x: x.get('title'))
    elif sort_query == "desc":
        goals_response.sort(key=lambda x: x.get('title'), reverse=True)

    return jsonify(goals_response)

# GET METHOD - get one goal by goal_id
@goal_bp.route("/<goal_id>", methods = ["GET"])
def get_by_goal_id(goal_id):
    goal = validate_model(Goal, goal_id)
    return {"goal": goal.to_dict()}, 200

# PUT METHOD - update goal by goal_id
@goal_bp.route("/<goal_id>", methods = ["PUT"])
def update_goal(goal_id):
    goal = validate_model(Goal,goal_id)

    request_body = request.get_json()
    goal.title = request_body["title"]

    db.session.commit()
    return jsonify({"goal": goal.to_dict()}), 200

# DELETE METHOD - delete a goal by goal_id
@goal_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal = validate_model(Goal, goal_id)
        
    db.session.delete(goal)
    db.session.commit()
    return { "details": f'Goal {goal_id} "{goal.title}" successfully deleted'}



# POST METHOD - post adds a list of task_ids to a goal
@goal_bp.route("/<goal_id>/tasks", methods = ["POST"])
def add_tasks_to_existing_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    request_body = request.get_json()
    task_ids = request_body["task_ids"]

    for id in task_ids:
        task = validate_model(Task,id)
        goal.tasks.append(task)

    db.session.commit()
    return {
        "id": goal.goal_id,
        "task_ids": task_ids
    }

# GET METHOD - reads all tasks for goal id
@goal_bp.route("/<goal_id>/tasks", methods = ["GET"])
def read_all_tasks_for_goal_id(goal_id):
    goal = validate_model(Goal, goal_id)
    task_response = []

    # for task in goal.tasks:
    #     task_response.append(task.to_dict())
    task_response =[task.to_dict() for task in goal.tasks]

    return jsonify({
        "id": goal.goal_id,
        "title": goal.title,
        "tasks": task_response
    }), 200






# slack bot task completed notification
# https://www.mechanicalgirl.com/post/building-simple-slack-app-using-flask/
# https://api.slack.com/methods/chat.postMessage/test
# https://realpython.com/getting-started-with-the-slack-api-using-python-and-flask/
# https://stackoverflow.com/questions/41546883/what-is-the-use-of-python-dotenv
# https://slack.dev/python-slack-sdk/web/index.html
# https://github.com/SlackAPI/python-slack-sdk
# alternative method: use url and request.post() - will need Bearer
####################################
# PYTHON SLACK IMPLEMENTATION METHOD
####################################
# def slack_bot_notification(task):
#     from dotenv import load_dotenv
#     import os
    
#     load_dotenv()
#     slack_token= os.environ.get("SLACK_API_KEY")

#     from slack_sdk import WebClient
#     client = WebClient(token=slack_token)
#     # print(slack_token)

#     response = client.chat_postMessage(
#         channel="C056SCXBCJ3",
#         text = f"Someone just completed the task {task.title}" 
#         )


# sort query
# if filterby_query = True
# check for query
#### TESTING ######
# @goal_bp.route("", methods=["GET"])
# def get_all_goals():
#     goals_response = []
#     goals = Goal.query.all()

#     goals_response = [goal.to_dict() for goal in goals]
    
#     query_lst = check_query()

#     if query_lst:
#         goals_response = filter_by_query(goals, goals_response, query_lst)
        
#     goals_response = check_sort(goals_response)

#     # # https://www.programiz.com/python-programming/methods/list/sort
#     # sort_query = request.args.get("sort")
#     # if sort_query == "asc":
#     #     goals_response.sort(key=lambda x: x.get('title'))
#     # elif sort_query == "desc":
#     #     goals_response.sort(key=lambda x: x.get('title'), reverse=True)

#     return jsonify(goals_response)

# def check_query():
#     query_lst = []
#     sort_query = request.args.get("sort")
#     filter_query_by_title = request.args.get("title")
#     filter_query_by_id = request.args.get("id")

#     if sort_query:
#         query_lst.append(sort_query)
#     elif filter_query_by_title:
#         query_lst.append(filter_query_by_title)
#     elif filter_query_by_id:
#         query_lst.append(filter_query_by_id)

#     return query_lst

# def check_sort(lst):
#     sort_query = request.args.get("sort")

#     if sort_query == "asc":
#         return lst.sort(key=lambda x: x.get('title'))
#     elif sort_query == "desc":
#         return lst.sort(key=lambda x: x.get('title'), reverse=True)
#     return lst

