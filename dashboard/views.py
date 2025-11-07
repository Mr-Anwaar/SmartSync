from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages

from django.core.mail import EmailMessage
from django.conf import settings

import csv
import requests
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

from translator.openai_translation import translate
# local imports
from .forms import *
from .models import *
from .functions import *


# Create your views here.

@login_required
def home(request):
    emptyBlogs = []
    completedBlogs = []
    monthCount = 0
    blogs = Blog.objects.filter(profile=request.user.profile)
    for blog in blogs:
        sections = BlogSection.objects.filter(blog=blog)
        if sections.exists():
            # calculate the blog words
            blogWords = 0
            for section in sections:
                blogWords += int(section.wordCount)
                monthCount += int(section.wordCount)
            blog.wordCount = str(blogWords)
            blog.save()
            completedBlogs.append(blog)
        else:
            emptyBlogs.append(blog)

    context = {}
    context['numBlogs'] = len(completedBlogs)
    context['monthCount'] = str(monthCount)
    context['countReset'] = '12 July 2023'
    context['emptyBlogs'] = emptyBlogs
    context['completedBlogs'] = completedBlogs

    user = request.user
    if hasattr(user, 'profile'):
        pass
    else:
        profile = Profile.objects.create(user=user)

    return render(request, 'dashboard/home.html', context)


@login_required
def profile(request):
    context = {}

    if request.method == 'GET':
        form = ProfileForm(instance=request.user.profile, user=request.user)
        image_form = ProfileImageForm(instance=request.user.profile)
        context['form'] = form
        context['image_form'] = image_form
        return render(request, 'dashboard/profile.html', context)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile, user=request.user)
        image_form = ProfileImageForm(request.POST, request.FILES, instance=request.user.profile)

        if form.is_valid():
            form.save()
            return redirect('profile')
        if image_form.is_valid():
            image_form.save()
            return redirect('profile')

    return render(request, 'dashboard/profile.html', context)


def generateTranslation(request):
    context = {}

    if request.method == 'POST':
        # retrieving the blog idea string from the from which comes in the request.POST
        aiPrompt = request.POST['aiPrompt']

        # saving text blog idea in the session to access it later in another route
        request.session['aiPrompt'] = aiPrompt

        aiLanguage = request.POST['aiLanguage']
        request.session['aiLanguage'] = aiLanguage

        textTranslated = generateTranslation(aiLanguage, aiPrompt)
        if len(textTranslated) > 0:
            request.session['textTranslated'] = textTranslated
            return redirect('translation')
        else:
            messages.error(request, "Oops we could not generate any blog ideas for you, please try again")
            return redirect('translation')

    return render(request, 'translation/translation.html', context)


@login_required
def contentTopic(request):
    context = {}

    if request.method == 'POST':
        # retrieving the blog idea string from the from which comes in the request.POST
        contentIdea = request.POST['contentTopic']

        contentTopics = generateContent(contentIdea)
        if len(contentTopics) > 0:
            request.session['contentTopics'] = contentTopics

            if 'contentTopics' in request.session:
                # Start by saving the blog...
                content = Content.objects.create(
                    title=contentTopic,
                    body=contentTopics,
                    profile=request.user.profile)
                content.save()

            return redirect('view-content')

        else:
            messages.error(request, "Oops we could not generate any blog ideas for you, please try again")
            return redirect('generate-content')

    return render(request, 'dashboard/generate-content.html', context)


@login_required
def viewContent(request):
    if 'contentTopics' in request.session:
        pass
    else:
        messages.error(request, "Start by creating blog topic ideas")
        return redirect('generate-content')

    context = {}

    context['contentTopics'] = request.session['contentTopics']
    # print(context)
    return render(request, 'dashboard/view-content.html', context)


@login_required
def blogTopic(request):
    context = {}

    if request.method == 'POST':
        # retrieving the blog idea string from the from which comes in the request.POST
        blogIdea = request.POST['blogIdea']

        # saving text blog idea in the session to access it later in another route.
        request.session['blogIdea'] = blogIdea

        keywords = request.POST['keywords']
        request.session['keywords'] = keywords

        audience = request.POST['audience']
        request.session['audience'] = audience

        blogTopics = generateBlogTopicIdeas(blogIdea, audience, keywords)
        if len(blogTopics) > 0:
            request.session['blogTopics'] = blogTopics
            return redirect('blog-sections')
        else:
            messages.error(request, "Oops we could not generate any blog ideas for you, please try again")
            return redirect('blog-topic')

    return render(request, 'dashboard/blog-topic.html', context)


@login_required
def blogSections(request):
    if 'blogTopics' in request.session:
        pass
    else:
        messages.error(request, "Start by creating blog topic ideas")
        return redirect('blog-topic')

    context = {}

    context['blogTopics'] = request.session['blogTopics']

    return render(request, 'dashboard/blog-sections.html', context)


# function for deleting the topic
@login_required
def deleteBlogTopic(request, uniqueId):
    try:
        blog = Blog.objects.get(uniqueId=uniqueId)
        if blog.profile == request.user.profile:
            blog.delete()
            return redirect('dashboard')
        else:
            messages.error(request, "Access Denied")
            return redirect('dashboard')

    except:
        messages.error(request, "Blog not found")
        return redirect('dashboard')


# function for saving the topic
@login_required
def saveBlogTopic(request, blogTopic):
    if 'blogIdea' in request.session and 'keywords' in request.session and 'audience' in request.session and 'blogTopics' in request.session:

        blog = Blog.objects.create(
            title=blogTopic,
            blogIdea=request.session['blogIdea'],
            keywords=request.session['keywords'],
            audience=request.session['audience'],
            profile=request.user.profile)
        blog.save()

        blogTopics = request.session['blogTopics']
        blogTopics.remove(blogTopic)
        request.session['blogTopics'] = blogTopics

        return redirect('blog-sections')
    else:
        return redirect('blog-topic')


# function for using the topic
@login_required
def useBlogTopic(request, blogTopic):
    context = {}

    if 'blogIdea' in request.session and 'keywords' in request.session and 'audience' in request.session:
        # Start by saving the blog...
        blog = Blog.objects.create(
            title=blogTopic,
            blogIdea=request.session['blogIdea'],
            keywords=request.session['keywords'],
            audience=request.session['audience'],
            profile=request.user.profile)
        blog.save()

        blogSections = generateBlogSectionTitles(blogTopic, request.session['audience'], request.session['keywords'])
    else:
        return redirect('blog-topic')

    if len(blogSections) > 0:
        # adding sections to the sessions
        request.session['blogSections'] = blogSections

        # adding sections to the context
        context['blogSections'] = blogSections
    else:
        messages.error(request, "Oops you beat the AI, try again!")
        return redirect('blog-topic')

    if request.method == 'POST':
        for val in request.POST:
            if not 'csrfmiddlewaretoken' in val:  # Generating the blog section details
                section = generateBlogSectionDetails(blogTopic, val, request.session['audience'],
                                                     request.session['keywords'])
                # Create database record
                BlogSec = BlogSection.objects.create(
                    title=val,
                    body=section,
                    blog=blog)

                BlogSec.save()

        return redirect('view-generated-blog', slug=blog.slug)
    return render(request, 'dashboard/select-blog-sections.html', context)


# function for using the topic
@login_required
def createBlogFromTopic(request, uniqueId):
    context = {}

    try:
        blog = Blog.objects.get(uniqueId=uniqueId)
    except:
        messages.error(request, "Blog not found")
        return redirect('dashboard')

    blogSections = generateBlogSectionTitles(blog.title, blog.audience, blog.keywords)

    if len(blogSections) > 0:
        # adding sections to the sessions
        request.session['blogSections'] = blogSections

        # adding sections to the context
        context['blogSections'] = blogSections
    else:
        messages.error(request, "Oops you beat the AI, try again!")
        return redirect('blog-topic')

    if request.method == 'POST':
        for val in request.POST:
            if not 'csrfmiddlewaretoken' in val:  # Generating the blog section details
                section = generateBlogSectionDetails(blog.title, val, blog.audience, blog.keywords)
                # Create database record
                BlogSec = BlogSection.objects.create(
                    title=val,
                    body=section,
                    blog=blog)

                BlogSec.save()

        return redirect('view-generated-blog', slug=blog.slug)
    return render(request, 'dashboard/select-blog-sections.html', context)


@login_required
def viewGeneratedBlog(request, slug):
    try:
        blog = Blog.objects.get(slug=slug)
    except:
        messages.error(request, "Something Went Wrong")
        return redirect('blog-topic')

    # Fetch the created section for the blog
    blogSections = BlogSection.objects.filter(blog=blog)

    context = {}
    context['blog'] = blog
    context['blogSections'] = blogSections

    return render(request, 'dashboard/view-generated-blog.html', context)


@login_required
def dashboard_trans(request):
    if request.method == 'POST':
        text = request.POST['text']
        source_lang = request.POST['source_lang']
        target_lang = request.POST['target_lang']
        translated_text = translate(text, source_lang, target_lang)
    else:
        text = ''
        source_lang = 'en'
        target_lang = 'ur'
        translated_text = ''

    return render(request, 'dashboard/dashboard-trans.html', {
        'text': text,
        'source_lang': source_lang,
        'target_lang': target_lang,
        'translated_text': translated_text,
    })


# views.py

from django.shortcuts import render, redirect
from django.contrib import messages


from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage
from django.conf import settings
from django.shortcuts import render, redirect
from datetime import datetime
from .tasks import send_bulk_emails


@login_required
def bulk_email_sender(request):
    if request.method == 'POST':
        email_option = request.POST.get('email_option')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        if email_option == 'comma_separated':
            email_list = [email.strip() for email in request.POST.get('email_list', '').split(',') if email.strip()]
        elif email_option == 'csv_file':
            email_list = []
            csv_file = request.FILES.get('csv_file')
            if csv_file:
                try:
                    if not csv_file.name.endswith('.csv'):
                        messages.error(request, 'Please upload a CSV file.')
                        return redirect('bulk_email_sender')
                    reader = csv.reader(csv_file.read().decode('utf-8').splitlines())
                    for row in reader:
                        email_address = row[0] if len(
                            row) > 0 else ''  # Assuming the email address is in the first column
                        email_list.append(email_address.strip())
                        print(email_list)
                except Exception as e:
                    print(f"CSV processing error: {e}")
        else:
            email_list = []

        # Get the schedule date and time from the form
        schedule_date = request.POST.get('schedule_date')
        schedule_time = request.POST.get('schedule_time')

        attachment = request.FILES.get('attachments')
        saved_file_path = None

        if attachment:
            fs = FileSystemStorage()
            attachment.name=attachment.name.replace(" ","_")
            filename = fs.save(attachment.name, attachment)
            saved_file_path = filename
            print(saved_file_path)

        if schedule_date and schedule_time:
            schedule_datetime = datetime.strptime(schedule_date + ' ' + schedule_time, '%Y-%m-%d %H:%M')
            schedule_datetime = f"{schedule_datetime}+05:00"
            # Schedule the task to be executed at the specified date and time
            send_bulk_emails.apply_async(args=[email_list, subject, message, saved_file_path], eta=schedule_datetime)

            messages.success(request, 'Email scheduled for sending.')

        # Redirect to a success page or back to the form
        return redirect('bulk_email_sender')

    return render(request, 'dashboard/bulk_email_sender.html')


from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


@login_required
def deactivate_account(request):
    if request.method == 'POST':
        # Perform account deactivation logic here

        # Delete the user's account (User model record)
        user = request.user
        user.delete()

        # Logout the user to invalidate their session
        logout(request)

        # Redirect the user to the signup page after account deletion
        return redirect('register')  # Replace 'signup' with your signup page name or URL

    return render(request, 'profile.html')  # Render the profile page if it's a GET request


