from django.db import models


class Question(models.Model):
    question_text = models.CharField(max_length=64, default="Where shall we eat today?")
    pub_date = models.DateField('date published')

    def __str__(self):
        return "{} {} @ {}".format(self.id, self.question_text, self.pub_date)


class Restaurant(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return "{}".format(self.name)


class Employee(models.Model):
    name = models.CharField(max_length=64, unique=True)


class Menu(models.Model):
    pub_date = models.DateField('date published')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, unique_for_date="pub_date")
    choice_menu = models.FileField("menu file", unique_for_date="pub_date")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)


class Vote(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('employee', 'menu', )

