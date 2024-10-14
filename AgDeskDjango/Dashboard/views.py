from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from Tasks.models import Task
from datetime import datetime

from django.template.defaulttags import register
from .forms import addWidgetForm, myTasksDateForm
from .models import DashboardLayout, Widget
from .widgets import get_widget_instance, get_widget_class, get_updated_scope, MyTasks
from FarmAcc.views import FarmManager

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .widgets import MyCheckouts, weatherWidgetSmall
from assetOperation.views import get_user_current_checkouts_oldest
from django.core.serializers.json import DjangoJSONEncoder
from assetOperation.models import OperationLog
from .weatherAPI import WeatherManager

@login_required(login_url='login')
def mainDash(request, farm_id):

    #WeatherAPI configured on GET request
    weather = WeatherManager()

    weather.main()

    farmManager = FarmManager()
    current_user = request.user
    farmManager.set_user_current_farm_by_id(current_user, farm_id)

    dashboard, created = DashboardLayout.objects.get_or_create(farm=current_user.currentFarm)

    if created:
        create_default_dashboard(request.user, dashboard)

    if request.method == "POST":
        newWidgetForm = addWidgetForm(request.POST)
        if newWidgetForm.is_valid():
            widget_name = newWidgetForm.cleaned_data['widget_name']
            widget_instance = get_widget_instance(widget_name)
            if widget_instance:
                if widget_instance.type == "weatherWidgetSmall":
                    weatherData = weather.currentWeatherWidget(weather.getCurrLocation()['geographicLocation'])
                    widget_instance.set_data(request.user, weatherData = weatherData)
                elif widget_instance.type == "weatherWidgetWeek":
                    weatherData = weather.fiveDayForecastWidget(weather.getCurrLocation()['geographicLocation'])
                    widget_instance.set_data(request.user, weatherData = weatherData)
                else:
                    widget_instance.set_data(request.user)
                widget = Widget.objects.create(
                    name=widget_name,
                    type=widget_instance.type,
                    sizex = widget_instance.col,
                    sizey = widget_instance.row,
                    scope=widget_instance.get_context()
                )
                dashboard.widgets.add(widget)
                return JsonResponse({
                    'success': True,
                    'widget': {
                        'id': widget.id,
                        'name': widget.name,
                        'type': widget.type,
                        'sizex': widget.sizex,
                        'sizey': widget.sizey,
                        'scope': widget.scope,
                    }
                }, encoder=DjangoJSONEncoder)
            else:
                return JsonResponse({'success': False, 'error': 'Invalid widget type'}, status=400)
        return JsonResponse({'success': False, 'errors': newWidgetForm.errors}, status=400)

    context = {
        "addWidgetForm": addWidgetForm(),
        "myTasksDateForm": myTasksDateForm(),
        "dashboard": dashboard,
    }
    return render(request, "Dashboard/baseDash.html", context)


def create_default_dashboard(user, dashboard):
    default_widgets = ['My Tasks']

    for widget_name in default_widgets:
        widget_instance = get_widget_instance(widget_name)
        if widget_instance:
            widget_instance.set_data(user)
            widget = Widget.objects.create(
                name=widget_name,
                type=widget_instance.type,
                sizex = widget_instance.col,
                sizey = widget_instance.row,
                scope=widget_instance.get_context()
            )
            dashboard.widgets.add(widget)

    dashboard.save()


@csrf_exempt
def save_layout(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            layout_data = data.get('layout', [])
            widget_data = data.get('widgets', [])

            dashboard = DashboardLayout.objects.get(farm=request.user.currentFarm)
            dashboard.layout_data = layout_data
            dashboard.save()

            for widget in widget_data:
                Widget.objects.filter(id=widget['id']).update(
                    col=widget['col'],
                    row=widget['row'],
                    sizex=widget['sizex'],
                    sizey=widget['sizey']
                )

            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            return JsonResponse({
                'status' : 'error',
                'message': 'Invalid data'
            }, status=400)
    return JsonResponse({
        'status' : 'error',
        'message': 'Invalid request'
    }, status=400)


@csrf_exempt
def get_layout(request):
    if request.method == 'GET':
        try:
            dashboard = DashboardLayout.objects.get(farm=request.user.currentFarm)
            widgets = dashboard.widgets.all()

            widget_data = []
            for widget in widgets:
                widget_class = get_widget_class(widget.type)
                if widget_class:
                    widget_instance = widget_class()
                    updated_scope = get_updated_scope(widget.scope, request.user, widget_instance)
                    widget_data.append({
                        'id'   : widget.id    ,
                        'name' : widget.name  ,
                        'type' : widget.type  ,
                        'scope': updated_scope,
                        'col'  : widget.col   ,
                        'row'  : widget.row   ,
                        'sizex': widget.sizex ,
                        'sizey': widget.sizey
                    })

            return JsonResponse({
                'layout' : dashboard.layout_data,
                'widgets': widget_data
            })
        except DashboardLayout.DoesNotExist:
            return JsonResponse({
                "layout" : None,
                "widgets": None,
                "message": "Layout does not exist"
            })
    return JsonResponse({
        'status' : 'error',
        'message': 'Invalid request'
    }, status=400)


@login_required
@require_POST
@csrf_exempt
def delete_widget(request):
    widget_id = request.POST.get('widget_id')
    try:
        widget = Widget.objects.get(id=widget_id)
        dashboard = DashboardLayout.objects.get(farm=request.user.currentFarm)

        # Remove the widget from the dashboard
        dashboard.widgets.remove(widget)

        # Delete the widget
        widget.delete()

        # Save the dashboard to update its configuration
        dashboard.save()

        return JsonResponse({'success': True})
    except Widget.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Widget not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def update_my_tasks(request):
    date_str = request.POST.get('date')
    widgetId = request.POST.get('id')
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        widgetInstance = Widget.objects.get(id=widgetId)
        my_tasks_widget = MyTasks()
        updated_data = my_tasks_widget.set_data(request.user, date)
        widgetInstance.scope['data'] = updated_data
        widgetInstance.save()
        return JsonResponse({'success': True, 'data': updated_data})
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid date format'}, status=400)

@login_required
@require_POST
def checkin(request):
    log_id = request.POST.get('logID')
    notes = request.POST.get('notes')

    try:
        log = OperationLog.objects.get(logID=log_id, userID=request.user, endDateTime__isnull=True)
        log.endDateTime = datetime.now()
        log.notes = notes
        log.save()
        return JsonResponse({'success': True})
    except OperationLog.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Log not found or already checked in'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
@login_required
def get_my_checkouts(request):
    checkouts = get_user_current_checkouts_oldest(request.user)
    data = [
        {
            'label': checkout.assetID.assetName,
            'value': {
                'startTime': checkout.startDateTime.strftime("%d/%m/%y %I:%M %p"),
                'logID': checkout.logID,
                'logNotes': checkout.notes
            }
        }
        for checkout in checkouts
    ]
    return JsonResponse({'success': True, 'data': data})
    
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)