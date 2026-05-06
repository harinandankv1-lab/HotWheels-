from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    category = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
class User(models.Model):
    name = models.CharField(max_length=100)
    email=models.EmailField()
    password = models.CharField(max_length=10)
    address = models.CharField(max_length=200)
    phone=models.IntegerField()
    def __str__(self):
        return f"{self.name}"
    


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"
    
    from django.db import models

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey('User', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)

    quantity = models.IntegerField(default=1)
    total_price = models.IntegerField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.email}"
    
class Feedback(models.Model):
    RATING_CHOICES=[
        (1,'1'),
        (2,'2'),
        (3,'3'),
        (4,'4'),
        (5,'5'),
    ]
    feedback_text=models.TextField()
    rating=models.IntegerField(choices=RATING_CHOICES)
    created_at=models.DateTimeField(auto_now_add=True)
    email=models.EmailField()
    def __str__(self):
        return str(self.email)