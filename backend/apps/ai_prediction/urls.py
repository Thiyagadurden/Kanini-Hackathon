from django.urls import path
from . import views

urlpatterns = [
    # Risk prediction
    path('predict/', views.predict_risk, name='predict_risk'),
    path('explain/', views.explain_prediction, name='explain_prediction'),
    
    # RAG and document processing
    path('retrieve/', views.retrieve_context, name='retrieve_context'),
    path('document/', views.process_document, name='process_document'),
    path('query/', views.query_pipeline, name='query_pipeline'),
]
