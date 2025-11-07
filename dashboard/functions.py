import os
import openai
from django.conf import settings

# Load your API key from an environment variable or secret management service
openai.api_key = settings.OPENAI_API_KEY
openai.api_base= settings.OPENAI_API_BASE

def textTranslation(language, text):
    response = openai.Completion.create(
        model="TheBloke/Llama-2-7b-chat-fp16",
        prompt="Translate this into  {}:\n\n{}\n".format(language, text),
        temperature=0.7,
        max_tokens=500,
        top_p=1,
        best_of=1,
        frequency_penalty=0,
        presence_penalty=0)

    if 'choices' in response:
        if len(response['choices']) > 0:
            res = response['choices'][0]['text']
            cleanedRes = res.replace('\n', '<br>')
            return cleanedRes
        else:
            return ''
    else:
        return ''


def generateContent(contentTopic):
    response = openai.Completion.create(
        model="TheBloke/Llama-2-7b-chat-fp16",
        prompt=" {}\n * ".format(contentTopic),
        temperature=0.7,
        max_tokens=700,
        top_p=1,
        best_of=1,
        frequency_penalty=0,
        presence_penalty=0)

    if 'choices' in response:
        if len(response['choices']) > 0:
            res = response['choices'][0]['text']
            cleanedRes = res.replace('\n', '<br>')
            return cleanedRes
        else:
            return ''
    else:
        return ''


def generateBlogTopicIdeas(topic, audience, keywords):
    blog_topics = []

    response = openai.Completion.create(
        model="TheBloke/Llama-2-7b-chat-fp16",
        prompt="Generate 5 blog topic ideas on the given topic: {} \naudience: {} \nKeywords: {} \n*".format(topic,
                                                                                                             audience,
                                                                                                             keywords),
        temperature=0.7,
        max_tokens=250,
        top_p=1,
        best_of=1,
        frequency_penalty=0.1,
        presence_penalty=0)

    if 'choices' in response:
        if len(response['choices']) > 0:
            res = response['choices'][0]['text']
        else:
            return []
    else:
        return []

    # a list variable for splitting
    a_list = res.split('*')
    if len(a_list) > 0:
        for blog in a_list:
            blog_topics.append(blog)
    else:
        return []

    return blog_topics


# Generate blogs section after the given topic
def generateBlogSectionTitles(topic, audience, keywords):
    blog_sections = []

    response = openai.Completion.create(
        model="TheBloke/Llama-2-7b-chat-fp16",
        prompt="Generate 5 blog section titles for the provided blog topic: {} \naudience: {} \nKeywords: {} \n*".format(
            topic, audience, keywords),
        temperature=0.7,
        max_tokens=250,
        top_p=1,
        best_of=1,
        frequency_penalty=0,
        presence_penalty=0)

    if 'choices' in response:
        if len(response['choices']) > 0:
            res = response['choices'][0]['text']
        else:
            return []
    else:
        return []

    # a list variable for splitting
    a_list = res.split('*')
    if len(a_list) > 0:
        for blog in a_list:
            blog_sections.append(blog)
    else:
        return []

    return blog_sections


# Blog section details
def generateBlogSectionDetails(blogTopic, sectionTopic, audience, keywords):
    response = openai.Completion.create(
        model="TheBloke/Llama-2-7b-chat-fp16",
        prompt="Generate detailed blog section write up for the following blog section heading, using the blog title, audience and keywords provided: \n Blog title: {} \nBlog Selection Heading: {} \nAudience: {} \nKeywords: {} \n*".format(
            blogTopic, sectionTopic, audience, keywords),
        temperature=0.7,
        max_tokens=500,
        top_p=1,
        best_of=1,
        frequency_penalty=0,
        presence_penalty=0)

    if 'choices' in response:
        if len(response['choices']) > 0:
            res = response['choices'][0]['text']
            cleanedRes = res.replace('\n', '<br>')
            return cleanedRes
        else:
            return ''
    else:
        return ''
