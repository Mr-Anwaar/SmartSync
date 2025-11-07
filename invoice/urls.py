from django.urls import path
from . import views

urlpatterns = [
path('invoices/invoicedashboard', views.invoicedashboard, name='invoicedashboard'),
path('invoices/invoices', views.invoices, name='invoices'),
path('invoices/products', views.products, name='products'),
path('invoices/clients', views.clients, name='clients'),

#Create URL Paths
path('invoices/create', views.createInvoice, name='create-invoice'),
path('invoices/create-build/<slug:slug>', views.createBuildInvoice, name='create-build-invoice'),

#Delete an invoice
path('invoices/delete/<slug:slug>', views.deleteInvoice, name='delete-invoice'),

#PDF and EMAIL Paths
path('invoices/view-pdf/<slug:slug>', views.viewPDFInvoice, name='view-pdf-invoice'),
path('invoices/view-document/<slug:slug>', views.viewDocumentInvoice, name='view-document-invoice'),
path('invoices/email-document/<slug:slug>', views.emailDocumentInvoice, name='email-document-invoice'),

#Company Settings Page
path('invoice/company-settings', views.companySettings, name='company-settings'),
#path('delete-company/<int:company_id>/', views.delete_company, name='delete-company'),

#products page URLS
path('invoices/products/edit/<slug:slug>/', views.editProduct, name='edit-product'),
    # Define the product detail URL
path('invoices/products/<slug:slug>/', views.product_detail, name='product-detail'),
path('invoices/products/delete/<slug:slug>', views.delete_product, name='delete-product'),

#Client Page URLSs:
# Edit Client
path('invoices/clients/edit/<slug:slug>/', views.editClient, name='edit-client'),

    # Delete Client
path('invoices/clients/delete/<slug:slug>/', views.deleteClient, name='delete-client'),
]

