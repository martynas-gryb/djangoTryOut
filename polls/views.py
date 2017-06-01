import logging
from datetime import date

from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from .models import Question, Restaurant, Menu, Employee, Vote
from .forms import UploadFileForm


logger = logging.getLogger("django")

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def default(request):
    logger.debug("redirecting to today")
    return HttpResponseRedirect('/today/')

def index(request):
    logger.info("Index accessed from {}".format(get_client_ip(request)))
    question = todays_question()
    choices = Menu.objects.filter(question=question)
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
    logger.debug("Accessing todays question")
    today = date.today()
    # use the same day since it's inclusive
    question = Question.objects.filter(pub_date=today).first()
    if not question:
        logger.debug("there is no question yet, create it")
        question = Question.objects.create(pub_date=today)

    return question


# create restaurant
def create_restaurant(request, r_name):
    """
    Create restaurant and return it's id
    """
    restaurant = Restaurant.objects.create(name=r_name)
    logger.info("Creating restaurant {} from {}".format(r_name, get_client_ip(request)))
    return HttpResponse(str(restaurant.pk))


# download menu
def download_menu(request, m_id):
    menu = Menu.objects.get(pk=m_id)
    response = HttpResponse(menu.choice_menu, content_type="octet/stream")
    logger.info("Downloading menu {} from {}".format(m_id, get_client_ip(request)))
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
            logger.info("Uploading menu {} from {}".format(menu.pk, get_client_ip(request)))
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
    logger.info("creating employee {} from {}".format(e_name, get_client_ip(request)))
    return HttpResponse(str(employee.pk))


# vote for menu
def vote_for_restaurant_menu(request, r_id, e_id):
    """
    Create employee and return it's id
    """
    vote = Vote.objects.create(
        employee=get_object_or_404(Employee, pk=e_id),
        menu=Menu.objects.get(question=todays_question(),
                              restaurant=get_object_or_404(Restaurant, pk=r_id))
    )
    logger.info("voting with  employee {} for restaurant {} from {}".format(e_id,
                                                                            r_id,
                                                                            get_client_ip(request)))
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

    logger.info("getting todays results from {}".format(get_client_ip(request)))
    text = "Winner is {} with {} votes".format(
        Menu.objects.get(pk=winner["menu"]).restaurant,
        winner["vote_count"]
    )
    response = HttpResponse(text)
    return response