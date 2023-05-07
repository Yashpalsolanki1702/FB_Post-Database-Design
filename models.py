from django.db import models
from fb_post.Enums import ReactionEnum
from django.core.exceptions import ValidationError


def validate_reaction_enum(reaction):
    if reaction not in ReactionEnum.list_of_reaction_enum():
        raise ValidationError('Invalid Choice')


class User(models.Model):
    name = models.CharField(max_length=100)
    profile_pic = models.CharField(max_length=100)


class Group(models.Model):
    name = models.TextField(max_length=100)
    members = models.ManyToManyField(User, through='Membership')


class Post(models.Model):
    content = models.CharField(max_length=1000, null=True, blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)


class Comment(models.Model):
    content = models.CharField(max_length=1000, null=True, blank=True)
    commented_at = models.DateTimeField(auto_now_add=True)
    commented_by = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    parent_comment = models.ForeignKey('self',
                                       null=True, blank=True,
                                       on_delete=models.CASCADE)


class React(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)
    reaction = models.CharField(max_length=100,
                                validators=[validate_reaction_enum])
    reacted_at = models.DateField(auto_now_add=True)
    reacted_by = models.ForeignKey(User, on_delete=models.CASCADE)


class Membership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    member = models.ForeignKey(User,on_delete=models.CASCADE)
    is_admin = models.BooleanField()
