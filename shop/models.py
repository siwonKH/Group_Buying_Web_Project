from django.db import models


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(max_length=100)
    password = models.TextField(max_length=1000)
    salt = models.TextField(max_length=10)

    def __str__(self):
        return self.id


class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    id = models.IntegerField()
    name = models.TextField(max_length=1000)
    title = models.TextField(max_length=1000)
    price = models.TextField(max_length=20)
    image = models.ImageField(max_length=10000, upload_to='post_img', default='default.png')
    shop_link = models.TextField(max_length=10000, default=" ")
    content = models.TextField(max_length=10000, default=" ")
    signed_id = models.TextField(max_length=5000, null=True)
    signed_amount = models.TextField(max_length=5000, null=True)
    post_date = models.DateTimeField(auto_now_add=True, blank=True)
    post_end = models.DateTimeField(auto_now_add=False)

    def __str__(self):
        return self.id


class Stat(models.Model):
    id = models.IntegerField(primary_key=True)
    my_post = models.TextField(null=True, default="")
    my_signed_post = models.TextField(null=True, default="")
    my_signed_amount = models.TextField(null=True, default="")

    def __str__(self):
        return self.id
