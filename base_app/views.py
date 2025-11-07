from django.contrib.auth.decorators import login_required
from django.http import HttpResponseServerError, StreamingHttpResponse
from django.shortcuts import render
from .oai_queries import stream_response

DEFAULT_SYSTEM_PROMPT = """\
You are a helpful, respectful, and honest assistant. Always provide responses that are helpful, respectful, and safe. Avoid harmful, unethical, or offensive content. If a question is unclear or factually incorrect, kindly explain instead of providing incorrect information. If you are unsure, do not share false information."""


@login_required
def query_view(request):
    if request.method == 'POST':
        user_query = request.POST.get('prompt')
        output_in = request.POST.get('output_in')
        tone = request.POST.get('tone')
        writing_style = request.POST.get('writing_style')

        # Reinforce the language instruction in the prompt
        prompt = (
            f"{DEFAULT_SYSTEM_PROMPT}\n\n"
            f"You asked: '{user_query}'. Please provide a concise and engaging response related to the user's query. "
            f"Ensure proper formatting with HTML tags like <h1>, <h2>, and <p> for titles, subtitles, and paragraphs. "
            f"Write the output response in '{output_in}' language specifically. Maintain a '{tone}' tone and apply a '{writing_style}' writing style."
        )

        # Set the timeout for streaming response (adjust as needed)
        timeout_seconds = 900
        print(prompt)

        # Return a streaming response
        return StreamingHttpResponse(stream_response(prompt), content_type="text/event-stream")

    return render(request, 'dashboard/query.html')
