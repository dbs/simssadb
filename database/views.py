from django.shortcuts import render
from django.views.generic import (TemplateView, ListView, DetailView,
                                  CreateView, UpdateView, DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import PieceForm
from . import forms
from django.urls import reverse
from django.views.generic import ListView
from rest_framework import generics
from database.serializers import *

# Create your views here.


class HomeView(TemplateView):  # show about page
    template_name = 'home.html'


class AboutView(TemplateView):  # show about page
    template_name = 'about.html'

# This function
# searches for post_form page!
# you cannot create a post unless logged in


class CreatePieceView(LoginRequiredMixin, CreateView):
    login_url = '/login/'

    redirect_field_name = 'database/musicalwork_detail.html'  # save the new
    #  post, and it redirects to post_detail page

    form_class = PieceForm  # This creates a new PostForm,
    # and PostForm already specifies which fields we need to create
    model = MusicalWork


class MusicalWorkDetailView(DetailView):  # show the content
    # of the post when clicking
    model = MusicalWork  #


class MusicalWorkListView(ListView):  # home page: show a list of post
    model = MusicalWork  # what do you want to show
    # in this list: post, so model = Post


class SignUp(CreateView):
    form_class = forms.UserCreateForm

    def get_success_url(self):
        return reverse('login')
    # success_url = reverse('about.html')  # cause "circular import" problem
    template_name = "registration/signup.html"


class InstrumentDetail(generics.RetrieveAPIView):
    queryset = Instrument.objects.all()
    serializer_class = InstrumentSerializer


class GenreDetail(generics.RetrieveAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
