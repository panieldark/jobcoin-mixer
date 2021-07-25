from django.db import models

# Create your models here.



MIXER_STATUS_CHOICES = (
	('created', 'Created'),
	('in_progress', 'In Progress'),
	('completed', 'Completed'),
)
class MixerRequest(models.Model):
	src_address = models.CharField(max_length=50, default='', blank=True)
	dest_address = models.CharField(max_length=50, default='', blank=True)
	deposit_address = models.CharField(max_length=50, default='', blank=True)
	status = models.CharField(
		max_length=50, default='created', choices=MIXER_STATUS_CHOICES)

	def __str__(self):
		return f"Request from {self.src_address} to {self.dest_address}"
