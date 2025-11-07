# views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import *
from .models import *
from .functions import *
from django.contrib.auth.models import User
from random import randint
from uuid import uuid4
from django.http import HttpResponse
import pdfkit
from django.template.loader import get_template
import os

# Anonymous required
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings as django_settings
from django.core.mail import send_mail

def anonymous_required(function=None, redirect_url=None):
    if not redirect_url:
        redirect_url = 'dashboard'

    actual_decorator = user_passes_test(
        lambda u: u.is_anonymous,
        login_url=redirect_url
    )

    if function:
        return actual_decorator(function)
    return actual_decorator

@login_required
def index(request):
    try:
        settings = Settings.objects.get(user=request.user)
        client_name = settings.clientName
    except Settings.DoesNotExist:
        client_name = "Your Default Client Name"

    context = {
        'client_name': client_name,
        'user': request.user,  # Pass the authenticated user to the template
    }
    return render(request, 'layout/dashboard.html', context)

@login_required
def invoicedashboard(request):
    try:
        # Get the settings for the current user
        settings = Settings.objects.get(user=request.user)
        client_name = settings.clientName
    except Settings.DoesNotExist:
        # If settings not found for the user, redirect to company settings page
        return redirect('company-settings')

    # Filter clients and invoices based on the current user
    clients = Client.objects.filter(user=request.user).count()
    invoices = Invoice.objects.filter(client__user=request.user).count()
    paidInvoices = Invoice.objects.filter(client__user=request.user, status='PAID').count()
    print(client_name)
    print(settings)
    context = {
        'client_name': client_name,  # Pass the client name to the template
        'clients': clients,
        'invoices': invoices,
        'paidInvoices': paidInvoices
    }
    print(context)
    return render(request, 'invoice/invoicedashboard.html', context)
@login_required
def invoices(request):
    context = {}
    invoices = Invoice.objects.filter(user=request.user)
    context['invoices'] = invoices

    return render(request, 'invoice/invoices.html', context)

@login_required
def products(request):
    context = {}
    products = Product.objects.filter(user=request.user)
    context['products'] = products

    return render(request, 'invoice/products.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'invoice/product_detail.html', {'product': product})

@login_required
def editProduct(request, slug):
    # Retrieve the product to edit
    product = get_object_or_404(Product, slug=slug)

    if request.method == 'POST':
        # If the form was submitted, process the data
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('products')
    else:
        # If it's a GET request, create a form with the current product data
        form = ProductForm(instance=product)

    # Render the edit_product.html template with the form
    return render(request, 'invoice/edit_product.html', {'form': form, 'product': product})

@login_required
def delete_product(request, slug):
    product = get_object_or_404(Product, slug=slug, user=request.user)

    if request.method == 'POST':
        product.delete()
        return redirect('products')

    context = {'product': product}
    return render(request, 'invoice/delete_product.html', context)

@login_required
def clients(request):
    context = {}
    clients = Client.objects.filter(user=request.user)
    context['clients'] = clients

    if request.method == 'GET':
        form = ClientForm()
        context['form'] = form
        return render(request, 'invoice/clients.html', context)

    if request.method == 'POST':
        form = ClientForm(request.POST, request.FILES)

        if form.is_valid():
            client = form.save(commit=False)
            client.user = request.user  # Associate the client with the authenticated user
            client.save()

            messages.success(request, 'New Client Added')
            return redirect('clients')
        else:
            messages.error(request, 'Problem processing your request')
            return redirect('clients')

    return render(request, 'invoice/clients.html', context)

@login_required
def editClient(request, slug):
    client = get_object_or_404(Client, slug=slug, user=request.user)

    if request.method == 'POST':
        form = ClientForm(request.POST, request.FILES, instance=client)
        if form.is_valid():
            form.save()
            return redirect('clients')
    else:
        form = ClientForm(instance=client)

    return render(request, 'invoice/edit_client.html', {'form': form, 'client': client})

@login_required
def deleteClient(request, slug):
    client = get_object_or_404(Client, slug=slug, user=request.user)

    if request.method == 'POST':
        client.delete()
        return redirect('clients')

    context = {'client': client}
    return render(request, 'invoice/delete_client.html', context)

@login_required
def logout(request):
    auth.logout(request)
    return redirect('login')

###--------------------------- Create Invoice Views Start here --------------------------------------------- ###

@login_required
def createInvoice(request):
    number = 'INV-' + str(uuid4()).split('-')[1]
    newInvoice = Invoice.objects.create(number=number, user=request.user)
    newInvoice.save()

    inv = Invoice.objects.get(number=number)
    return redirect('create-build-invoice', slug=inv.slug)


@login_required
def createBuildInvoice(request, slug):
    try:
        invoice = Invoice.objects.get(slug=slug, user=request.user)
    except Invoice.DoesNotExist:
        messages.error(request, 'Invoice not found')
        return redirect('invoices')

    products = Product.objects.filter(invoice=invoice)

    # Fetch clients associated with the logged-in user
    clients = Client.objects.filter(user=request.user)

    context = {
        'invoice': invoice,
        'products': products,
        'clients': clients,
    }

    if request.method == 'GET':
        prod_form = ProductForm()
        inv_form = InvoiceForm(instance=invoice)

        # Pass the 'user' argument when initializing the client_form
        client_form = ClientSelectForm(initial_client=invoice.client, user=request.user)

        context['prod_form'] = prod_form
        context['inv_form'] = inv_form
        context['client_form'] = client_form
        return render(request, 'invoice/create-invoice.html', context)

    if request.method == 'POST':
        prod_form = ProductForm(request.POST)
        inv_form = InvoiceForm(request.POST, instance=invoice)

        # Pass the 'user' argument when initializing the client_form
        client_form = ClientSelectForm(request.POST, initial_client=invoice.client, instance=invoice, user=request.user)

        if prod_form.is_valid():
            obj = prod_form.save(commit=False)

            # Set the user field for the product to the logged-in user
            obj.user = request.user

            obj.invoice = invoice
            obj.save()

            messages.success(request, "Invoice product added successfully")
            return redirect('create-build-invoice', slug=slug)
        elif inv_form.is_valid and 'paymentTerms' in request.POST:
            inv_form.save()

            messages.success(request, "Invoice updated successfully")
            return redirect('create-build-invoice', slug=slug)
        elif client_form.is_valid() and 'client' in request.POST:
            client_form.save()
            messages.success(request, "Client added to invoice successfully")
            return redirect('create-build-invoice', slug=slug)
        else:
            context['prod_form'] = prod_form
            context['inv_form'] = inv_form
            context['client_form'] = client_form
            messages.error(request, "Problem processing your request")
            return render(request, 'invoice/create-invoice.html', context)

    return render(request, 'invoice/create-invoice.html', context)


def viewPDFInvoice(request, slug):
    #fetch that invoice
    try:
        invoice = Invoice.objects.get(slug=slug, user=request.user)
        pass
    except:
        messages.error(request, 'Something went wrong')
        return redirect('invoices')

    #fetch all the products - related to this invoice
    products = Product.objects.filter(invoice=invoice)

    #Get Client Settings
    p_settings = Settings.objects.get(user=request.user)

    #Calculate the Invoice Total
    invoiceCurrency = ''
    invoiceTotal = 0.0
    if len(products) > 0:
        for x in products:
            y = float(x.quantity) * float(x.price)
            invoiceTotal += y
            invoiceCurrency = x.currency



    context = {}
    context['invoice'] = invoice
    context['products'] = products
    context['p_settings'] = p_settings
    context['invoiceTotal'] = "{:.2f}".format(invoiceTotal)
    context['invoiceCurrency'] = invoiceCurrency

    return render(request, 'invoice/invoice-template.html', context)

def viewDocumentInvoice(request, slug):
    # fetch that invoice
    try:
        invoice = Invoice.objects.get(slug=slug, user=request.user)
        pass
    except:
        messages.error(request, 'Something went wrong')
        return redirect('invoices')

    # fetch all the products - related to this invoice
    products = Product.objects.filter(invoice=invoice)

    # Get Client Settings
    p_settings = Settings.objects.first()

    # Calculate the Invoice Total
    invoiceTotal = 0.0
    if len(products) > 0:
        for x in products:
            y = float(x.quantity) * float(x.price)
            invoiceTotal += y

    context = {}
    context['invoice'] = invoice
    context['products'] = products
    context['p_settings'] = p_settings
    context['invoiceTotal'] = "{:.2f}".format(invoiceTotal)

    # The name of your PDF file
    filename = '{}.pdf'.format(invoice.uniqueId)

    # HTML FIle to be converted to PDF - inside your Django directory
    template = get_template('invoice/pdf-template.html')

    # Render the HTML
    html = template.render(context)

    # Options - Very Important [Don't forget this]
    options = {
        'encoding': 'UTF-8',
        'javascript-delay': '10',  # Optional
        'enable-local-file-access': None,  # To be able to access CSS
        'page-size': 'A4',
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ],
    }
    # Javascript delay is optional

    # Remember that location to wkhtmltopdf
    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

    # IF you have CSS to add to template
    css1 = os.path.join(settings.CSS_LOCATION, 'assets', 'css', 'bootstrap.min.css')
    css2 = os.path.join(settings.CSS_LOCATION, 'assets', 'css', 'dashboard.css')

    # Create the file
    file_content = pdfkit.from_string(html, False, configuration=config, options=options)

    # Create the HTTP Response
    response = HttpResponse(file_content, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename = {}'.format(filename)

    # Return
    return response


def emailDocumentInvoice(request, slug):
    # fetch that invoice
    try:
        invoice = Invoice.objects.get(slug=slug, user=request.user)
        pass
    except:
        messages.error(request, 'Something went wrong')
        return redirect('invoices')

    # fetch all the products - related to this invoice
    products = Product.objects.filter(invoice=invoice)

    # Get Client Settings
    p_settings = Settings.objects.first()

    # Calculate the Invoice Total
    invoiceTotal = 0.0
    if len(products) > 0:
        for x in products:
            y = float(x.quantity) * float(x.price)
            invoiceTotal += y

    context = {}
    context['invoice'] = invoice
    context['products'] = products
    context['p_settings'] = p_settings
    context['invoiceTotal'] = "{:.2f}".format(invoiceTotal)

    # The name of your PDF file
    filename = '{}.pdf'.format(invoice.uniqueId)

    # HTML FIle to be converted to PDF - inside your Django directory
    template = get_template('invoice/pdf-template.html')

    # Render the HTML
    html = template.render(context)

    # Options - Very Important [Don't forget this]
    options = {
        'encoding': 'UTF-8',
        'javascript-delay': '1000',  # Optional
        'enable-local-file-access': None,  # To be able to access CSS
        'page-size': 'A4',
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ],
    }
    # Javascript delay is optional

    # Remember that location to wkhtmltopdf
    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

    # Saving the File
    filepath = os.path.join(settings.MEDIA_ROOT, 'client_invoices')
    os.makedirs(filepath, exist_ok=True)
    pdf_save_path = filepath + filename
    # Save the PDF
    pdfkit.from_string(html, pdf_save_path, configuration=config, options=options)

    # send the emails to client
    to_email = invoice.client.emailAddress
    from_client = p_settings.clientName
    emailInvoiceClient(to_email, from_client, pdf_save_path)

    invoice.status = 'EMAIL_SENT'
    invoice.save()

    # Email was send, redirect back to view - invoice
    messages.success(request, "Email sent to the client succesfully")
    return redirect('create-build-invoice', slug=slug)


def deleteInvoice(request, slug):
    try:
        Invoice.objects.get(slug=slug, user=request.user).delete()
    except:
        messages.error(request, 'Something went wrong')
        return redirect('invoices')

    return redirect('invoices')

@login_required
def companySettings(request):
    try:
        # Try to retrieve the company settings for the current user
        company_settings = Settings.objects.get(user=request.user)
    except Settings.DoesNotExist:
        # If settings don't exist for the user, create new settings
        company_settings = Settings(user=request.user)

    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES, instance=company_settings)
        if form.is_valid():
            company_settings = form.save()
            return redirect('company-settings')

    context = {'company_settings': company_settings, 'form': SettingsForm(instance=company_settings)}
    return render(request, 'invoice/company-settings.html', context)
# Additional view to delete the user's company settings
