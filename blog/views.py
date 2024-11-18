from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Client, Equipement
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from .forms import EquipementForm, ClientForm

def client_management(request):
    equipements = Equipement.objects.prefetch_related('emprunteurs').all()
    clients = Client.objects.prefetch_related('emprunts').all()
    return render(request, 'blog/management.html', {
        'equipements': equipements,
        'clients': clients
    })

def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    equipements_disponibles = Equipement.objects.filter(state='disponible')

    if request.method == "POST":
        # Vérifier si c'est un emprunt d'équipement
        if 'equipement' in request.POST:
            equipement_id = request.POST.get('equipement')
            if equipement_id:
                try:
                    with transaction.atomic():
                        equipement = get_object_or_404(Equipement, pk=equipement_id)
                        date_retour = timezone.now() + timezone.timedelta(days=7)
                        equipement.emprunter(client, date_retour)
                        messages.success(request, "L'équipement a été emprunté avec succès.")
                except ValidationError as e:
                    messages.error(request, str(e))
            return redirect('client_detail', pk=client.pk)
        
        # Sinon, c'est une modification du client
        else:
            form = ClientForm(request.POST, request.FILES, instance=client)
            if form.is_valid():
                form.save()
                messages.success(request, "Les modifications ont été enregistrées.")
                return redirect('client_detail', pk=client.pk)
    else:
        form = ClientForm(instance=client)

    return render(request, 'blog/client_detail.html', {
        'client': client, 
        'form': form,
        'emprunts_actifs': client.get_emprunts_actifs(),
        'equipements_disponibles': equipements_disponibles
    })
def nouveau_client(request):
    if request.method == "POST":
        form = ClientForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    client = form.save()
                    messages.success(request, "Le client a été créé avec succès.")
                    return redirect('client_management')
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = ClientForm()
    return render(request, 'blog/nouveau_client.html', {'form': form})

def equipement_detail(request, pk):
    equipement = get_object_or_404(
        Equipement.objects.prefetch_related('emprunts__client'), 
        pk=pk
    )
    emprunt_actif = equipement.emprunts.filter(date_retour_effective=None).first()

    clients = Client.objects.all()
    
    return render(request, 'blog/equipement_detail.html', {
        'equipement': equipement,
        'emprunt_actif': emprunt_actif,
        'clients': clients })

def nouveau_equipement(request):
    if request.method == "POST":
        form = EquipementForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    equipement = form.save(commit=False)
                    equipement.save()

                    client_id = request.POST.get('client')
                    if client_id and equipement.state == 'occupé':
                        client = get_object_or_404(Client, pk=client_id)
                        date_retour = timezone.now() + timezone.timedelta(days=7)
                        equipement.emprunter(client, date_retour)

                    messages.success(request, "L'équipement a été créé avec succès.")
                    return redirect('client_management')
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = EquipementForm()

    clients = Client.objects.all()
    return render(request, 'blog/nouveau_equipement.html', {
        'form': form,
        'clients': clients
    })

def emprunter_equipement(request, pk):
    if request.method == "POST":
        equipement = get_object_or_404(Equipement, pk=pk)
        client_id = request.POST.get('client')
        date_retour = request.POST.get('date_retour')
        
        try:
            with transaction.atomic():
                client = get_object_or_404(Client, pk=client_id)
                date_retour = timezone.datetime.strptime(date_retour, '%Y-%m-%d')
                equipement.emprunter(client, date_retour)
                messages.success(request, "L'équipement a été emprunté avec succès.")
        except ValidationError as e:
            messages.error(request, str(e))
            
    return redirect('equipement_detail', pk=pk)

def retourner_equipement(request, pk):
    if request.method == "POST":
        equipement = get_object_or_404(Equipement, pk=pk)
        try:
            equipement.retourner()
            messages.success(request, "L'équipement a été retourné avec succès.")
        except ValidationError as e:
            messages.error(request, str(e))
    return redirect(request.META.get('HTTP_REFERER', 'client_management'))

def supprimer_equipement(request, pk):
    if request.method == "POST":
        equipement = get_object_or_404(Equipement, pk=pk)
        try:
            with transaction.atomic():
                equipement.delete()
                messages.success(request, "L'équipement a été supprimé avec succès.")
                return redirect('client_management')  # Redirection vers la page principale
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('client_management')