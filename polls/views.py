from datetime import date

from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Max
from django.http import HttpResponse, HttpResponseRedirect
from .models import Question, Restaurant, Menu, Employee, Vote
from .forms import UploadFileForm


def index(request):
    question = todays_question()
    choices = Menu.objects.filter(question=question)
    print(choices)
    context = {
        'question': question,
        'choices': choices,
    }
    return render(request, template_name='polls/index.html', context=context)


def todays_question():
    """
    Get today's question, if not found create a new one
    :return: question object
    """
    today = date.today()
    # use the same day since it's inclusive
    question_set = Question.objects.filter(pub_date__range=[today, today])
    if not len(question_set):
        print("there is no question yet, create it")
        question = Question.objects.create(pub_date=today)
    else:
        print("returning question from db")
        question = question_set[0]

    return question


# create restaurant
def create_restaurant(request, r_name):
    """
    Create restaurant and return it's id
    """
    restaurant = Restaurant.objects.create(name=r_name)
    return HttpResponse(str(restaurant.pk))


# download menu
def download_menu(request, m_id):
    menu = Menu.objects.get(pk=m_id)
    response = HttpResponse(menu.choice_menu, content_type="octet/stream")
    return response


# upload menu
def upload_menu(request, r_id):
    """
    Create restaurant and return it's id
    """
    if request.method == 'POST':
        restaurant = Restaurant.objects.get(pk=r_id)
        question = todays_question()
        today = date.today()
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            payload = request.FILES['menuFile']
            menu = Menu.objects.create(restaurant=restaurant,
                                       pub_date=today,
                                       question=question,
                                       choice_menu=payload)
            return HttpResponseRedirect('/today')
        else:
            return HttpResponse("invalid file")
    else:
        # display upload form
        return render(request, template_name='polls/file.html', context={})



# create employee
def create_employee(request, e_name):
    """
    Create employee and return it's id
    """
    employee = Employee.objects.create(name=e_name)
    return HttpResponse(str(employee.pk))


# vote for menu
def vote_for_restaurant_menu(request, r_id, e_id):
    """
    Create employee and return it's id
    """
    vote = Vote.objects.create(
        employee=get_object_or_404(Employee, pk=e_id),
        menu=Menu.objects.get(question=todays_question(), restaurant=get_object_or_404(Restaurant, pk=r_id))
    )
    return HttpResponse(str(vote.id))


# get today's result
def todays_result(request):
    """
    Get restaurant title with most votes
    """
    question = todays_question()
    menus = Menu.objects.filter(question=question)

    winner = Vote.objects.filter(menu__in=menus)\
        .values('menu')\
        .annotate(vote_count=Count('employee'))\
        .order_by('-vote_count')\
        .first()

    return HttpResponse("Winner is {} with {} votes".format(
        Menu.objects.get(pk=winner["menu"]).restaurant,
        winner["vote_count"]
    ))