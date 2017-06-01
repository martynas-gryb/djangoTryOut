from datetime import date
import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from .models import Question, Employee, Restaurant, Vote

from .views import todays_question


def cleanup_files_after_function(decorated):
    def wrapper(*args, **kwargs):
        output = decorated(*args, **kwargs)
        # after returning clean up junk files
        for item in os.listdir():
            if "testFile_" in item:
                os.remove(item)
        return output
    return wrapper


# Create your tests here.
class AllTheTests(TestCase):
    def test_todays_question(self):
        today = date.today()
        # assert that question does not exist
        self.assertRaises(Question.DoesNotExist, Question.objects.get, pub_date=today)
        question = todays_question()
        # assert that question was created
        try:
            Question.objects.get(pub_date=today)
        except Question.DoesNotExist:
            self.fail("Should already exist")

        # assert is the same instance
        self.assertIsInstance(question, Question)
        # assert is today
        pub_date = question.pub_date
        self.assertEqual(pub_date, today)
        # assert returns the same when called a second time
        question2 = todays_question()
        self.assertEqual(question, question2)

    def test_create_employee(self):
        name = 'RamunasK'
        url = reverse('create_e', args=(name,))
        try:
            Employee.objects.get(name=name)
        except Employee.DoesNotExist:
            # should be not found
            pass
        # create employee
        self.client.get(url)
        # can't create the same employee again
        self.assertRaises(Exception, self.client.get, url=url)

        try:
            Employee.objects.get(name=name)
        except Employee.DoesNotExist:
            self.fail("should exist")

    def test_create_restaurant(self):
        name = 'Soya'
        url = reverse('create_r', args=(name,))
        try:
            Restaurant.objects.get(name=name)
        except Restaurant.DoesNotExist:
            # should be not found
            pass
        # create restaurant
        self.client.get(url)
        # can't create the same employee again
        self.assertRaises(Exception, self.client.get, url=url)

        try:
            Restaurant.objects.get(name=name)
        except Restaurant.DoesNotExist:
            self.fail("should exist")

    @cleanup_files_after_function
    def test_create_menu(self):
        # test if can create menu
        name = 'Soya'
        url = reverse('create_r', args=(name,))
        self.client.get(url)
        restaurant = Restaurant.objects.get(name=name)

        url2 = reverse('upload', args=(restaurant.id,))

        with open('testFile') as fl:
            self.client.post(url2, {"menuFile": fl})

    @cleanup_files_after_function
    def test_can_vote(self):
        # create employee
        name = 'RamunasK'
        url = reverse('create_e', args=(name,))
        self.client.get(url)
        employee = Employee.objects.get(name=name)
        # create restaurant
        name = 'Soya'
        url = reverse('create_r', args=(name,))
        self.client.get(url)
        restaurant = Restaurant.objects.get(name=name)

        url = reverse('upload', args=(restaurant.id,))
        with open('testFile') as fl:
            self.client.post(url, {"menuFile": fl})

        url = reverse('vote_for', args=(restaurant.id, employee.id))
        self.client.get(url)
        try:
            Vote.objects.get(employee_id=employee.id)
        except Vote.DoesNotExist:
            self.fail("Voting failed")

    @cleanup_files_after_function
    def test_winner(self):
        # create employee
        name = 'RamunasK'
        url = reverse('create_e', args=(name,))
        self.client.get(url)
        employee = Employee.objects.get(name=name)
        # create restaurant
        winner = 'Soya'
        url = reverse('create_r', args=(winner,))
        self.client.get(url)
        restaurant = Restaurant.objects.get(name=winner)

        url = reverse('upload', args=(restaurant.id,))
        with open('testFile') as fl:
            self.client.post(url, {"menuFile": fl})

        url = reverse('vote_for', args=(restaurant.id, employee.id))
        self.client.get(url)
        try:
            vote = Vote.objects.get(employee_id=employee.id)
        except Vote.DoesNotExist:
            self.fail("Voting failed")

        url = reverse('winner')
        response = self.client.get(url)
        if not response or not response.content or winner not in str(response.content):
            self.fail("Winner not found")

