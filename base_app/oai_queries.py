# Import necessary modules
import time
from django.conf import settings
import openai
from django.http import StreamingHttpResponse, JsonResponse

# OpenAI API Key
if settings.OPENAI_API_KEY:
    openai.api_key = settings.OPENAI_API_KEY
    openai.api_base = settings.OPENAI_API_BASE
else:
    raise Exception('OpenAI API Key not found')

def stream_response(prompt):
    try:
        # Record the time before the request is sent
        start_time = time.time()

        # Send a Completion request with stream=True
        response = openai.Completion.create(
            model='TheBloke/Llama-2-7b-chat-fp16',
            prompt=prompt,
            max_tokens=1000,
            temperature=0.2,
            EarlyStopping=True,
            stream=True,  # Set stream=True to enable streaming
        )

        # Create variables to collect the stream of events
        collected_events = []
        completion_text = ''

        # Iterate through the stream of events
        for event in response:
            event_time = time.time() - start_time  # Calculate the time delay of the event
            collected_events.append(event)  # Save the event response
            event_text = event['choices'][0]['text']  # Extract the text
            completion_text += event_text  # Append the text
            yield event_text  # Yield the text as part of the streaming response

        # Print the time delay and text received
        #print(f"Full response received {event_time:.2f} seconds after request")
        #print(f"Full text received: {completion_text}")

    except openai.error.OpenAIError as e:
        yield "An error occurred while processing your request."
    except Exception as ex:
        yield "An unexpected error occurred."

def content_generator(request):
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '')

        # Return a streaming response
        return StreamingHttpResponse(stream_response(prompt), content_type="text/event-stream")
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
