"""
Views for the task and kanban board functionality.
"""


# Imports
from django.contrib.auth.decorators import login_required
# from django.contrib.sessions.models import Session
# from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
# from django.urls import reverse
# from django.views import View
from django.forms.models import model_to_dict

from UserAuth.models import UserProfile

from .forms import createTaskForm, taskForm, createKanbanForm, deleteKanbanForm, createKanbanContentForm, updateKanbanContentForm
from .models import Task, Kanban, KanbanContents

# from datetime import datetime
import json

# Task Manager
class taskManager():
    """
    Enables a user to manage tasks, including creation, updating and deletion.
    implements various task Forms
    """

    def getTasks(self, user):
        """
        Returns the tasks assigned to the current user
        """

        tasks = Task.objects \
            .filter(assignedTo=user.id, isDeleted=False, farmID=user.currentFarm) \
            .values() \
            .order_by('dueDate')

        if len(tasks) == 0:
            return ""

        for i, t in enumerate(tasks):
            try:
                tasks[i]['status'] = Task.TASK_STATUS_CHOICES[t['status']][1]
                tasks[i]['dueDate'] = tasks[i]['dueDate'].strftime("%d/%m/%Y")
            except IndexError as err:
                print(err)
                return ""

        return tasks
    
    def getTasksByDate(self, user, date):
        """
        Returns the tasks assigned to the current user
        """

        tasks = Task.objects \
            .filter(assignedTo=user.id, isDeleted=False, farmID=user.currentFarm, dueDate = date) \
            .values() \
            .order_by('dueDate')

        if len(tasks) == 0:
            return ""

        for i, t in enumerate(tasks):
            try:
                tasks[i]['status'] = Task.TASK_STATUS_CHOICES[t['status']][1]
                tasks[i]['dueDate'] = tasks[i]['dueDate'].strftime("%d/%m/%Y")
            except IndexError as err:
                print(err)
                return ""

        return tasks

    def createTask(self, request, taskData):
        """
        creates a new task entry in the database.

        (docstring needed rewrite, sorry.)
        """

        taskData["farmID"] = request.user.currentFarm
        if taskData["assignedTo"] == "":
            taskData["assignedTo"] = request.user.id

        Task.objects.create(**taskData)
        # .save() seemed to want to have a taskID provided, even though this is a new entry and
        # therefore is supposed to be auto incremented, so using create here instead.
        # The double asterisk (**) designates that taskData is a set of kwargs, which is some
        # really cool syntax I can't wait to abuse.

    def updateTask(self, taskID: int, taskData: dict):
        """
        Updates a specific single task in the database.

        (Docstring needed rewrite, sorry.)
        """

        targetTask = Task.objects.get(taskID=taskID)

        # Update all provided fields
        for key, val in taskData.items():
            setattr(targetTask, key, val)

        targetTask.save()

    def deleteTask(self, taskID):
        """
        Soft deletes a task from the database by setting `isDelete = True`
        """

        targetTask = Task.objects.get(taskID=taskID)
        targetTask.isDeleted = True
        targetTask.save()

        # Remove the task from kanban boards
        kanbanContents = KanbanContents.objects.filter(taskID=taskID).delete()


# Task Views
def taskTableManagement(request):
    taskManagement = taskManager()
    creationForm = createTaskForm(request.user)

    if request.method == "POST":
        creationForm = createTaskForm(request.user, request.POST)

        if creationForm.is_valid():
            taskManagement.createTask(request, creationForm.cleaned_data)

            return redirect("/tasks/tableView")

    tasks = taskManagement.getTasks(request.user)

    context = {
        "creationForm": creationForm,
        "TaskData"    : tasks
    }

    return render(request, "Tasks/taskTable.html", context)


def taskUpdatePage(request, taskID: int):
    # No idea what this does.
    if request.method == "GET":
        redirectURL= request.META.get('HTTP_REFERER')
        request.session['http_referer'] = redirectURL

    if not Task.objects.filter(taskID=taskID).exists():
        return HttpResponseRedirect(request.session['http_referer'])

    if request.method == "POST":
        taskManagement = taskManager()

        if "deleteTaskForm" in request.POST:
            taskManagement.deleteTask(taskID)

            return HttpResponseRedirect(request.session['http_referer'])

        updateTaskModal = taskForm(request.user, request.POST)

        if updateTaskModal.is_valid():
            taskManagement.updateTask(taskID, updateTaskModal.cleaned_data)

            # return HttpResponseRedirect(reverse("tableView"))
            return HttpResponseRedirect(request.session['http_referer'])

    targetTask = Task.objects.get(taskID=taskID)
    targetTask.dueDate = targetTask.dueDate.strftime("%d/%m/%Y")
    updateTaskModal = taskForm(request.user, initial=model_to_dict(targetTask))

    context = {
        "updateForm": updateTaskModal,
        "targTask": targetTask,
    }

    return render(request, "Tasks/updateTask.html", context=context)


def nullTaskUpdatePage(request):
    return redirect("/tasks/tableView")


# Kanbans
# I ought to use a manager class
@login_required
def kanbanTable(request):
    """
    A page containing a table of all the kanban boards.
    """

    if request.method =="POST":
        # Apparently I decided to do this differently?
        if "deleteKanbanForm" in request.POST:
            pass

        kanbanForm = createKanbanForm(request.POST)

        if kanbanForm.is_valid():
            newKanban = kanbanForm.cleaned_data
            newKanban["farmID"] = request.user.currentFarm

            Kanban.objects.create(**newKanban)

    # Query the database
    kanbanQuerySet = Kanban.objects.filter(farmID=request.user.currentFarm_id, deleted=False)
    kanbanContentsQuerySet = KanbanContents.objects.all()

    # Initialise all the counters
    statuses = {}
    for kanban in kanbanQuerySet:
        statuses[kanban.kanbanID] = [0] * 5

    # Count the number of tasks of each status per kanban board
    for content in kanbanContentsQuerySet:
        statuses[content.kanbanID.kanbanID][content.taskID.status] += 1

    # Pull the data together
    kanbans = [
        tuple([kanban.kanbanID, kanban.name] + statuses[kanban.kanbanID])
        for kanban in kanbanQuerySet
    ]

    # Render page with the data
    context = {
        "Kanbans": kanbans,
        "createKanbanForm": createKanbanForm
    }

    return render(request, "Tasks/kanbanTable.html", context)


@login_required
def kanbanBoard(request):
    """
    A page viewing a singular kanban board.
    """

    curKanbanID = request.COOKIES.get('curKanbanID') # Omitting URL params, for better or worse
    # Should really add an error message if the cookie doesn't exist

    kanban = Kanban.objects.get(kanbanID=curKanbanID)
    kanbanContentsQuerySet = KanbanContents.objects.filter(kanbanID=curKanbanID)

    name = kanban.name
    bucketNames = ["Not Started", "In Progress", "Blocked", "Review", "Complete"]
    cardInfoList = [
        (
            content.taskID.status             ,
            content.order                     ,
            content.taskID.taskID             ,
            content.taskID.name               ,
            content.taskID.description        ,
            content.taskID.assignedTo.username # Where is this username from?!
        )
        for content in kanbanContentsQuerySet
        if content.taskID.status < 5
    ]
    cardInfoList = sorted(cardInfoList, key = lambda x: (x[0], x[1]))

    # Get the unused tasks
    kanbanTaskIDs = [content.taskID.taskID for content in kanbanContentsQuerySet]
    taskQuerySet = Task.objects.filter(
        isDeleted=False, farmID=request.user.currentFarm
    ).values(
        "taskID"     ,
        "status"     ,
        "name"       ,
        "description",
        "assignedTo"
    )
    tasks = list(taskQuerySet)
    utasks = [task for task in tasks if task["taskID"] not in kanbanTaskIDs]
    utasks = sorted(utasks, key=lambda x: x["name"])
    for idx, task in enumerate(utasks):
        utasks[idx]["assignedTo"] = UserProfile.objects.get(id=task["assignedTo"]).username

    # Build context
    context = {
        "Name"   : name   ,
        "UTasks" : utasks ,
        "BucketNames": bucketNames,
        "CardInfoList": cardInfoList
    }

    return render(request, "Tasks/kanbanView.html", context)


@login_required
def deleteKanban(request):
    if request.method == "POST":
        deleteKanbanByID(int(request.POST["kanbanID"]))

        # Form didn't want to work
        # kanbanForm = deleteKanbanForm(request.POST)
        # if kanbanForm.is_valid():
        #     kanbanID = kanbanForm.cleaned_data["kanbanID"]
        #     deleteKanbanByID(kanbanID)

        return redirect("/tasks/kanbanTable")


@login_required
def updateKanban(request):
    """
    Updating the kanban board.

    Desired format
        cards: [
            {
                taskID:int,
                order :int,
                status:int
            }
        ]
    """

    if request.method == 'POST':
        # Get the json asap, no point processing anything else if this is going to fail
        # Should probably do validation here, everything just needs to be a integer
        #   (taskID > 0 and order >= 0 and status >= 0)
        try:
            newKanbanContentsList = json.loads(request.POST.get("cards"))
        except json.JSONDecodeError:
            return JsonResponse({
                'status' : 'error',
                'message': 'Invalid data'
            }, status=400)
        newKanbanContentsList = sorted(newKanbanContentsList, key=lambda x: x["taskID"])

        curKanbanID = request.COOKIES.get('curKanbanID')
        kanbanContentsQuerySet = KanbanContents.objects \
            .filter(kanbanID=curKanbanID).order_by("taskID")
        oldKanbanContentsList = list(kanbanContentsQuerySet)

        # Update the state of the kanban, content by content
        while len(newKanbanContentsList) + len(oldKanbanContentsList) > 0:
            # Slightly redundent elifs and poor if conditions, but I wanted this explicit
            if   len(oldKanbanContentsList) == 0:
                createKanbanContents(newKanbanContentsList, oldKanbanContentsList, curKanbanID)
            elif len(newKanbanContentsList) == 0:
                deleteKanbanContents(newKanbanContentsList, oldKanbanContentsList)
            elif newKanbanContentsList[0]["taskID"] <  oldKanbanContentsList[0].taskID.taskID:
                createKanbanContents(newKanbanContentsList, oldKanbanContentsList, curKanbanID)
            elif newKanbanContentsList[0]["taskID"] >  oldKanbanContentsList[0].taskID.taskID:
                deleteKanbanContents(newKanbanContentsList, oldKanbanContentsList)
            elif newKanbanContentsList[0]["taskID"] == oldKanbanContentsList[0].taskID.taskID:
                updateKanbanContents(newKanbanContentsList, oldKanbanContentsList)
            else:
                print("Something has gone horrifically wrong in Tasks.views.updateKanban.")

        return JsonResponse({'success': True})

    return JsonResponse({
        'status' : 'error',
        'message': 'Invalid request'
    }, status=400)


# Move these into a manager classes?
def deleteKanbanByID(kanbanID):
    kanban = Kanban.objects.get(kanbanID=kanbanID)
    kanban.deleted = True
    kanban.save()

def createKanbanContents(newKanbanContentsList, _, curKanbanID):
    """
    Create a new kanbanContents, a relation between a task and a Kanban board.
    """

    newKanbanContent = newKanbanContentsList.pop(0)

    newKanbanContentInstance = KanbanContents(
        kanbanID = Kanban.objects.get(kanbanID=curKanbanID),
        taskID   = Task.objects.get(taskID=newKanbanContent["taskID"]),
        order    = newKanbanContent["order" ]
    )
    newKanbanContentInstance.save()

    task = Task.objects.get(
        taskID = newKanbanContent["taskID"]
    )
    task.status = newKanbanContent["status"]
    task.save()

    # formData = createKanbanContentForm(
    #     newKanbanContent["taskID"],
    #     newKanbanContent["order" ],
    #     newKanbanContent["status"]
    # )

    # if formData.is_valid():
    #     createKanbanContents(curKanbanID, formData.cleaned_data)


def updateKanbanContents(newKanbanContentsList, oldKanbanContentsList):
    """
    Update an already existing kanbanContents.
    """

    oldKanbanContent = oldKanbanContentsList.pop(0)
    newKanbanContent = newKanbanContentsList.pop(0)

    content = KanbanContents.objects.get(kanbanContentsID=oldKanbanContent.kanbanContentsID)
    content.order = newKanbanContent["order"]
    content.save()

    task = Task.objects.get(taskID=content.taskID.taskID)
    task.status = newKanbanContent["status"]
    task.save()

    # formData = updateKanbanContentForm(
    #     oldKanbanContent["kanbanContentsID"],
    #     newKanbanContent["order"           ],
    #     newKanbanContent["status"          ]
    # )

    # if formData.is_valid():


def deleteKanbanContents(_, oldKanbanContentsList):
    """
    Delete a kanbanContents off the face of the Earth, forever.
    """

    oldKanbanContent = oldKanbanContentsList.pop(0)

    KanbanContents.objects.get(kanbanContentsID=oldKanbanContent.kanbanContentsID).delete()
    # Might be able to just go `oldKanbanContent.delete()`

    # No form validation, the data handled here comes from the database instead of the client.


# Not used
def getUTasks(request):
    """
    API endpoint that returns the unused tasks for a kanban board.
    'Unused' meaning that the task isn't currently in the board.

    This is intended to be run from the kanbanView.html page.
    """

    if request.method == 'GET':
        try:
            curKanbanID = request.COOKIES.get("curKanbanID")
            kanbanContentIDsQuerySet = KanbanContents.objects.filter(
                kanbanID=curKanbanID
            ).values("kanbanID")
            kanbanContentIDs = list(kanbanContentIDsQuerySet)

            taskQuerySet = Task.objects.get(
                isDeleted=False, farmID=request.user.currentFarm
            ).values(
                "taskID"     ,
                "status"     ,
                "name"       ,
                "description",
                "assignedTo"
            )
            tasks = list(taskQuerySet)
            utasks = [task for task in tasks if task["taskID"] not in kanbanContentIDs]

            return JsonResponse({
                'utasks': utasks
            })

        except Exception as err:
            return JsonResponse({
                "message": "Something screwed up",
                "error": err
            })

    return JsonResponse({
        'status' : 'error',
        'message': 'Invalid request'
    }, status=400)
