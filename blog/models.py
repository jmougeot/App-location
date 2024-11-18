from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class Client(models.Model):
    adresse = models.CharField(max_length=100, default='Inconnu')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()
    created_datedate = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='clients/')

    def get_emprunts_actifs(self):
        return self.emprunts.filter(date_retour_effective=None)

    def __str__(self):
        return self.name

class Equipement(models.Model): 
    STATE_CHOICES = [
        ('occupé', 'Occupé'),
        ('disponible', 'Disponible'),
        ('endommagé', 'Endommagé'),
    ]
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=100, choices=STATE_CHOICES, default='disponible')
    emprunteurs = models.ManyToManyField(
        Client,
        through='Emprunt',
        related_name='equipements_empruntes'
    )    
    category = models.CharField(max_length=100)
    image = models.ImageField(upload_to='equipements/')

    def est_disponible(self):
        return self.state == 'disponible'

    def emprunter(self, client, date_retour_prevue):
        if not self.est_disponible():
            raise ValidationError("Cet équipement n'est pas disponible")
        
        self.state = 'occupé'
        self.save()
        
        return Emprunt.objects.create(
            client=client,
            equipement=self,
            date_retour_prevue=date_retour_prevue
        )

    def retourner(self):
        emprunt_actif = self.emprunts.filter(date_retour_effective=None).first()
        if emprunt_actif:
            emprunt_actif.date_retour_effective = timezone.now()
            emprunt_actif.save()
            
        self.state = 'disponible'
        self.save()

    def __str__(self):
        return self.name

class Emprunt(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='emprunts')
    equipement = models.ForeignKey(Equipement, on_delete=models.CASCADE, related_name='emprunts')
    date_emprunt = models.DateTimeField(default=timezone.now)
    date_retour_prevue = models.DateTimeField()
    date_retour_effective = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['equipement', 'date_emprunt']

    def est_en_retard(self):
        return (not self.date_retour_effective and 
                timezone.now() > self.date_retour_prevue)

    def __str__(self):
        return f"{self.client.name} - {self.equipement.name}"