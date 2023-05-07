from fb_post.models import User, Post, Comment, React, Group, Membership
from fb_post.exceptions import *
from fb_post.Enums import ReactionEnum
from django.db.models import Count, F, Value, Sum, Avg, Max, Min, Count

from django.db.models import Q
from typing import (
    Dict,
    List,
    Any,
)


def validate_user_id(user_id: int):
    try:
        User.objects.get(id=user_id)

    except User.DoesNotExist:
        raise InvalidUserException


def validate_post_content(post_content: str):
    if len(post_content) == 0:
        raise InvalidPostException


def validate_comment_content(comment_content: str):
    if len(comment_content) == 0:
        raise InvalidCommentContent


def validate_post_id(post_id: int):
    try:
        Post.objects.get(id=post_id)

    except Post.DoesNotExist:
        raise InvalidPostException


def validate_comment_id(comment_id: int):
    try:
        Comment.objects.get(id=comment_id)

    except Comment.DoesNotExist:
        raise InvalidCommentContent


def validate_reply_content(reply_content: str):
    if len(reply_content) == 0:
        raise InvalidReplyContent


def validate_reaction(reaction_type: str):
    if reaction_type not in ReactionEnum.list_of_reaction_enum():
        raise InvalidReactionTypeException


def validate_group_name(name: str):
    if len(name) == 0:
        raise InvalidGroupNameException


def validate_member(member_ids: List[int]):
    existing_member_ids = list(User.objects.filter(id__in=member_ids
                                                   ).values_list('id',
                                                                 flat=True))

    if list(set(member_ids)) != list(set(existing_member_ids)):
        raise InvalidMemberException


def validate_group_id(group_id: int):
    try:
        Group.objects.get(id=group_id)

    except Group.DoesNotExist:
        raise InvalidGroupException


def validate_user_id_in_group(user_id: int, group_id: int):
    try:
        Membership.objects.get(group_id=group_id, member_id=user_id)

    except Membership.DoesNotExist:
        raise UserNotInGroupException


def validate_user_as_admin(user_id: int, group_id: int):
    try:
        Membership.objects.filter(group_id=group_id,
                                  member_id=user_id).get(
            is_admin=True)

    except Membership.DoesNotExist:
        raise UserIsNotAdminException


# Task2
# 1 sql query
def create_post(user_id: int, post_content: str, group_id=None) -> int:
    validate_user_id(user_id)
    validate_post_content(post_content)

    if group_id != None:
        validate_group_id(group_id)
        validate_user_id_in_group(user_id, group_id)

    post_object = Post.objects.create(content=post_content,
                                      posted_by_id=user_id,
                                      group_id=group_id)

    return post_object.id


'''Input: create_post(2,'Whatsup')
    output: post_id=18 '''


# Task3
# 1 sql query
def create_comment(user_id: int, post_id: int, comment_content: str) -> int:
    validate_user_id(user_id)
    validate_post_id(post_id)
    validate_comment_content(comment_content)

    comment_object = Comment.objects.create(content=comment_content,
                                            commented_by_id=user_id,
                                            post_id=post_id)

    return comment_object.id


'''Input: create_comment(4,15,'great')
    Output: comment_id=12'''


# Task4
# 1 sql query
def reply_to_comment(user_id: int, comment_id: int, reply_content: str) -> int:
    validate_user_id(user_id)
    validate_comment_id(comment_id)
    validate_reply_content(reply_content)

    reply_object = Comment.objects.create(content=reply_content,
                                          commented_by_id=user_id,
                                          parent_comment_id=comment_id)
    return reply_object.id


'''Input: reply_to_comment(5,7,'beautiful')
   Output: 11'''


# Task5
# 1 sql query
# Write a function to react to a post

def react_to_post(user_id: int, post_id: int, reaction_type: str):
    validate_user_id(user_id)
    validate_post_id(post_id)
    validate_reaction(reaction_type)
    reaction_object = React.objects.filter(
        reacted_by_id=user_id,
        post_id=post_id
    )

    if len(reaction_object) != 0:
        if reaction_object[0].reaction == reaction_type:
            reaction_object[0].delete()

        else:
            reaction_object[0].reaction = reaction_type
            reaction_object[0].save()
    else:
        React.objects.create(post_id=post_id,
                             reaction=reaction_type,
                             reacted_by_id=user_id)


# Task6
# 1 sql query

def react_to_comment(user_id: int, comment_id: int, reaction_type: str):
    validate_user_id(user_id)
    validate_comment_id(comment_id)
    validate_reaction(reaction_type)
    reaction_object = React.objects.filter(
        reacted_by_id=user_id,
        comment_id=comment_id
    )

    if len(reaction_object) != 0:
        if reaction_object[0].reaction == reaction_type:
            reaction_object[0].delete()

        else:
            reaction_object[0].reaction = reaction_type
            reaction_object[0].save()
    else:
        React.objects.create(comment_id=comment_id,
                             reaction=reaction_type,
                             reacted_by_id=user_id)


# Task7 -
# 1 sql query
def get_total_reaction_count() -> int:
    react_queryset = React.objects.aggregate(count=Count('reaction'))

    return react_queryset


'''Output: {'count': 23} '''


# Task8
def get_reaction_metrics(post_id: int) -> dict:
    react_queryset = React.objects.select_related('post').filter(
        post_id=post_id).values('reaction').annotate(
        reaction_count=Count('reaction'))

    ans_dict = {each_dict["reaction"]: each_dict["reaction_count"
    ] for each_dict in react_queryset}

    return ans_dict


'''Input: post_id= 14
    Output: {'LIT': 1, 'LOVE': 3, 'WOW': 1} '''


# Task9
# 1 sql query

def delete_post(user_id: int, post_id: int):
    pass
    validate_user_id(user_id)
    validate_post_id(post_id)

    queryset = Post.objects.filter(Q(posted_by_id=user_id), Q(id=post_id))

    if len(queryset) == 0:
        raise UserCannotDeletePostException

    else:
        queryset.delete()


# Task10 -
# 1 sql query

def get_posts_with_more_positive_reactions() -> List[int]:
    queryset = Post.objects.prefetch_related('react_set').values(
        'react__reaction').annotate(
        positive_reaction_count=Count('react__reaction', filter=Q(
            react__reaction__in=['THUMBS_UP', 'LIT', 'LOVE', 'HAHA', 'WOW'])),
        negative_reaction_count=Count('react__reaction', filter=Q(
            react__reaction__in=['SAD', 'ANGRY', 'THUMBS_DOWN']))).annotate(
        diff=F('positive_reaction_count') - F(
            'negative_reaction_count')).filter(diff__gte=1).values(
        'id').distinct()

    list_of_ids = [id_dict['id'] for id_dict in queryset]

    return list_of_ids


'''Output: [14, 17, 27, 28, 15, 12, 16]'''


# Task11
# 2 sql queries

def get_posts_reacted_by_user(user_id: int) -> List[int]:
    validate_user_id(user_id)
    list_of_post_ids = list(Post.objects.prefetch_related('react_set').filter(
        react__reacted_by_id=user_id).values_list('id', flat=True))

    return list_of_post_ids


'''Input: user_id=3 
   Output: [14,17,27,28] '''

# Task12
# 2 sql queries
'''The function should return all the reactions of the given post_id as a
list of dictionaries'''


def get_reactions_to_post(post_id: int) -> List[Dict[str, Any]]:
    validate_post_id(post_id)
    queryset = React.objects.select_related('post', 'reacted_by').filter(
        post_id=post_id)

    list_of_user_reaction_dicts = [
        {
            'user_id': react_obj.reacted_by.id,
            'name': react_obj.reacted_by.name,
            'profile_pic': react_obj.reacted_by.profile_pic,
            'reaction': react_obj.reaction
        }
        for react_obj in queryset]

    return list_of_user_reaction_dicts


'''Input: post_id= 14        
    Output:[{'user_id': 3, 'name': 'user 3', 'profile_pic': '3rd', 
                                                            'reaction': 'WOW'},
 {'user_id': 2, 'name': 'user 2', 'profile_pic': '2nd', 'reaction': 'LOVE'},
 {'user_id': 1, 'name': 'user 1', 'profile_pic': '1st', 'reaction': 'LOVE'},
 {'user_id': 5, 'name': 'user5', 'profile_pic': 'lo', 'reaction': 'LOVE'},
 {'user_id': 6, 'name': 'user6', 'profile_pic': 'better', 'reaction': 'LIT'}]

'''


# Task13
# Write a function to get the details of a given post.

def get_post(post_id: int) -> List[Dict[str, Any]]:
    validate_post_id(post_id)

    post_queryset = Post.objects.filter(id=post_id).select_related(
        'posted_by').prefetch_related(
        'react_set').annotate(reaction_count=Count('react__reaction')
                              )

    comment_queryset = Comment.objects.filter(post_id=post_id).select_related(
        'commented_by', 'post').prefetch_related('comment_set', 'react_set',
                                                 'comment_set__commented_by',
                                                 'comment_set__react_set',
                                                 ).annotate(
        reaction_count=Count('react__reaction')
    )

    list_of_posts = []
    for post in post_queryset:
        post_dict = {
            'post_id': post.id,
            'posted_by': {'name': post.posted_by.name,
                          'user_id': post.posted_by.id,
                          'profile_pic': post.posted_by.profile_pic
                          },
            'posted_at': post.posted_at,
            'post_content': post.content}
        list_of_reaction_on_post = []

        for reaction_obj in post.react_set.all():
            list_of_reaction_on_post.append(reaction_obj.reaction)

        post_dict['reactions'] = {
            'count': post.reaction_count,
            'type': list(set(list_of_reaction_on_post))
        }

        list_of_comments = []
        for comment in comment_queryset:
            comment_dict = {
                'comment_id': comment.id,
                'commenter': {'user_id': comment.commented_by.id,
                              'name': comment.commented_by.name,
                              'profile_pic':
                                  comment.commented_by.profile_pic
                              },
                'commented_at': comment.commented_at,
                'comment_content': comment.content}

            list_of_reaction_on_comment = []
            for reaction_obj in comment.react_set.all():
                list_of_reaction_on_comment.append(reaction_obj.reaction)
            comment_dict['reactions'] = {
                'count': comment.reaction_count,
                'type': list(set(list_of_reaction_on_comment))
            }

            list_of_replies = []
            reply_objects = comment.comment_set.all()
            for reply in reply_objects:
                reply_dict = {
                    'reply_id': reply.id,
                    'commenter': {'user_id': reply.commented_by.id,
                                  'name': reply.commented_by.name,
                                  'profile_pic':
                                      reply.commented_by.profile_pic
                                  },
                    'commented_at': reply.commented_at,
                    'comment_content': reply.content}

                list_of_reaction_on_reply = []
                for reaction_obj in reply.react_set.all():
                    list_of_reaction_on_reply.append(reaction_obj.reaction)
                list_of_replies.append(reply_dict)

            list_of_comments.append(comment_dict)
            comment_dict['replies'] = list_of_replies

        post_dict['comments'] = list_of_comments
        list_of_posts.append(post_dict)

    return list_of_posts


'''input: post_id=14

    Output: 
[{'post_id': 14,
'posted_by': {'name': 'user 3', 'user_id': 3, 'profile_pic': '3rd'},
'posted_at': datetime.datetime(2023, 2, 13, 10, 48, 34, 65339, tzinfo=<UTC>),
'post_content': '',
'reactions': {'count': 5, 'type': ['LOVE', 'LIT', 'WOW']},
'comments': [{'comment_id': 5,
'commenter': {'user_id': 6, 'name': 'user6', 'profile_pic': 'better'},
'commented_at': datetime.datetime(2023, 2, 14, 11, 44, 52, 390873,
 tzinfo=<UTC>),
'comment_content': 'super',
'reactions': {'count': 1, 'type': ['WOW']},
'replies_count': 1,
'replies': [{'reply_id': 8,
  'commenter': {'user_id': 6, 'name': 'user6', 'profile_pic': 'better'},
  'commented_at': datetime.datetime(2023, 2, 14, 11, 46, 15, 123081, 
  tzinfo=<UTC>),
  'comment_content': 'thanks',
  'reactions': {'count': 1, 'type': ['LOVE']}}]},
{'comment_id': 6,
'commenter': {'user_id': 7, 'name': 'user7', 'profile_pic': 'better'},
'commented_at': datetime.datetime(2023, 2, 14, 11, 45, 8, 404534, 
tzinfo=<UTC>),
'comment_content': 'super duper',
'reactions': {'count': 0, 'type': []},
'replies_count': 1,
'replies': [{'reply_id': 9,
  'commenter': {'user_id': 7, 'name': 'user7', 'profile_pic': 'better'},
  'commented_at': datetime.datetime(2023, 2, 14, 11, 46, 41, 344167, 
  tzinfo=<UTC>),
  'comment_content': 'thanks bro',
  'reactions': {'count': 1, 'type': ['LOVE']}}]},
{'comment_id': 7,
'commenter': {'user_id': 8, 'name': 'user8', 'profile_pic': 'better'},
'commented_at': datetime.datetime(2023, 2, 14, 11, 45, 34, 500512,
 tzinfo=<UTC>),
'comment_content': 'awesome',
'reactions': {'count': 2, 'type': ['LOVE', 'LIT']},
'replies_count': 1,
'replies': [{'reply_id': 10,
  'commenter': {'user_id': 8, 'name': 'user8', 'profile_pic': 'better'},
  'commented_at': datetime.datetime(2023, 2, 14, 11, 47, 8, 832203, 
  tzinfo=<UTC>),
  'comment_content': 'okk',
  'reactions': {'count': 1, 'type': ['LIT']}}]}]}]
'''


# Task14
def get_user_posts(user_id: int) -> List[Dict[str, Any]]:
    validate_user_id(user_id)

    post_queryset = Post.objects.filter(posted_by_id=user_id).select_related(
        'posted_by').prefetch_related(
        'react_set').annotate(reaction_count=Count('react__reaction')
                              )

    comment_queryset = Comment.objects.filter(
        commented_by_id=user_id).select_related(
        'commented_by', 'post').prefetch_related('comment_set', 'react_set',
                                                 'comment_set__commented_by',
                                                 'comment_set__react_set',
                                                 ).annotate(
        reaction_count=Count('react__reaction')
    )

    list_of_posts = []
    for post in post_queryset:
        post_dict = {
            'post_id': post.id,
            'posted_by': {'name': post.posted_by.name,
                          'user_id': post.posted_by.id,
                          'profile_pic': post.posted_by.profile_pic
                          },
            'posted_at': post.posted_at,
            'post_content': post.content}

        if not post.group:
            post_dict['group'] = None

        if post.group:
            post_dict['group'] = {
                'group_id': post.group_id,
                'name': post.group.name
            }

        list_of_reaction_on_post = []

        for reaction_obj in post.react_set.all():
            list_of_reaction_on_post.append(reaction_obj.reaction)

        post_dict['reactions'] = {
            'count': post.reaction_count,
            'type': list(set(list_of_reaction_on_post))
        }

        list_of_comments = []
        for comment in comment_queryset:
            comment_dict = {
                'comment_id': comment.id,
                'commenter': {'user_id': comment.commented_by.id,
                              'name': comment.commented_by.name,
                              'profile_pic':
                                  comment.commented_by.profile_pic
                              },
                'commented_at': comment.commented_at,
                'comment_content': comment.content}

            list_of_reaction_on_comment = []
            for reaction_obj in comment.react_set.all():
                list_of_reaction_on_comment.append(reaction_obj.reaction)
            comment_dict['reactions'] = {
                'count': comment.reaction_count,
                'type': list(set(list_of_reaction_on_comment))
            }

            list_of_replies = []
            reply_objects = comment.comment_set.all()
            for reply in reply_objects:
                reply_dict = {
                    'reply_id': reply.id,
                    'commenter': {'user_id': reply.commented_by.id,
                                  'name': reply.commented_by.name,
                                  'profile_pic':
                                      reply.commented_by.profile_pic
                                  },
                    'commented_at': reply.commented_at,
                    'comment_content': reply.content}

                list_of_reaction_on_reply = []
                for reaction_obj in reply.react_set.all():
                    list_of_reaction_on_reply.append(reaction_obj.reaction)
                list_of_replies.append(reply_dict)

            list_of_comments.append(comment_dict)
            comment_dict['replies'] = list_of_replies

        post_dict['comments'] = list_of_comments
        list_of_posts.append(post_dict)

    return list_of_posts


'''Input: user_id =3 
Output:
 
 [{'post_id': 11,
'posted_by': {'name': 'user 3', 'user_id': 3, 'profile_pic': '3rd'},
'posted_at': datetime.datetime(2023, 2, 13, 9, 39, 28, 340372, tzinfo=<UTC>),
'post_content': 'post_content',
'reactions': {'count': 0, 'type': []},
'comments': []},
{'post_id': 12,
'posted_by': {'name': 'user 3', 'user_id': 3, 'profile_pic': '3rd'},
'posted_at': datetime.datetime(2023, 2, 13, 9, 40, 16, 149659, tzinfo=<UTC>),
'post_content': '',
'reactions': {'count': 1, 'type': ['WOW']},
'comments': []},
{'post_id': 14,
'posted_by': {'name': 'user 3', 'user_id': 3, 'profile_pic': '3rd'},
'posted_at': datetime.datetime(2023, 2, 13, 10, 48, 34, 65339, tzinfo=<UTC>),
'post_content': '',
'reactions': {'count': 5, 'type': ['LIT', 'LOVE', 'WOW']},
'comments': []},
{'post_id': 15,
'posted_by': {'name': 'user 3', 'user_id': 3, 'profile_pic': '3rd'},
'posted_at': datetime.datetime(2023, 2, 13, 10, 49, 16, 317645, tzinfo=<UTC>),
'post_content': '',
'reactions': {'count': 1, 'type': ['LOVE']},
'comments': []},
{'post_id': 16,
'posted_by': {'name': 'user 3', 'user_id': 3, 'profile_pic': '3rd'},
'posted_at': datetime.datetime(2023, 2, 13, 10, 52, 38, 210403, tzinfo=<UTC>),
'post_content': '',
'reactions': {'count': 1, 'type': ['WOW']},
'comments': []}]

'''


# Task15
def get_replies_for_comment(comment_id: int) -> List[Dict[str, Any]]:
    validate_comment_id(comment_id)
    list_of_replies = []
    reply_objs = Comment.objects.filter(parent_comment_id=comment_id
                                        ).select_related(
        'commented_by').prefetch_related('react_set').annotate(
        react_count=Count('react__reaction'))

    for reply in reply_objs:
        reply_dict = {
            'reply_id': reply.id,
            'commenter': {'user_id': reply.commented_by.id,
                          'name': reply.commented_by.name,
                          'profile_pic':
                              reply.commented_by.profile_pic
                          },
            'commented_at': reply.commented_at,
            'comment_content': reply.content
        }

        list_of_replies.append(reply_dict)

    return list_of_replies


'''Input: comment_id=6
   Output: 
   [
      {'reply_id': 9,
       'commenter':
                {'user_id': 7, 
                 'name': 'user7',
                 'profile_pic': 'better'
                 },
      'commented_at': datetime.datetime(
                                2023, 2, 14, 11, 46, 41, 344167, tzinfo=<UTC>),
      'comment_content': 'thanks bro'
      }
  ]
'''


# Task 2

def create_group(user_id: int, name: str, member_ids: List[int]) -> int:
    validate_user_id(user_id)
    validate_group_name(name)
    validate_member(member_ids)

    group_obj = Group.objects.create(name=name)
    user_objs = User.objects.filter(id__in=member_ids)

    list_of_member_objs = [
        Membership(group=group_obj, member=user, is_admin=False)
        for user in user_objs]

    Membership.objects.bulk_create(list_of_member_objs)

    admin_obj = User.objects.get(id=user_id)
    Membership.objects.create(group=group_obj, member=admin_obj, is_admin=True)
    return group_obj.id


'''Input:  create_group(2,'Group6',[8,7,6])
   Output:  19 '''


# Task3

def add_member_to_group(user_id: int, new_member_id: int, group_id: int):
    validate_user_id(user_id)
    validate_user_id(new_member_id)
    validate_group_id(group_id)
    validate_user_id_in_group(user_id, group_id)
    validate_user_as_admin(user_id, group_id)

    if new_member_id != user_id:
        if new_member_id not in list(
                Membership.objects.filter(group_id=group_id).values_list(
                    'member', flat=True)):
            new_member_object = User.objects.get(id=new_member_id)

            m_obj = Membership.objects.create(group_id=group_id,
                                              member=new_member_object,
                                              is_admin=False)


'''Input():  add_member_to_group(2,5,19) '''


# Task 4

def remove_member_from_group(user_id: int, member_id: int, group_id: int):
    validate_user_id(user_id)
    validate_user_id(member_id)
    validate_group_id(group_id)
    validate_user_id_in_group(user_id, group_id)
    validate_user_id_in_group(member_id, group_id)
    validate_user_as_admin(user_id, group_id)

    Membership.objects.get(group_id=group_id,
                           member_id=member_id).delete()


'''input: remove_member_from_group(2,5,19) '''


# Task 5

def make_member_as_admin(user_id: int, member_id: int, group_id: int):
    validate_user_id(user_id)
    validate_user_id(member_id)
    validate_group_id(group_id)
    validate_user_id_in_group(user_id, group_id)
    validate_user_id_in_group(member_id, group_id)
    validate_user_as_admin(user_id, group_id)

    Membership.objects.filter(group_id=group_id, member_id=member_id).update(
        is_admin=True)


''' make_member_as_admin(2,8,19) '''


# Task 7

def get_group_feed(user_id: int, group_id: int, offset: int, limit: int):
    validate_user_id(user_id)
    validate_group_id(group_id)
    validate_user_id_in_group(user_id, group_id)

    if offset < 0:
        raise InvalidOffSetValueException

    if limit <= 0:
        raise InvalidLimitValueException

    post_queryset = Post.objects.filter(group_id=group_id,
                                        posted_by_id=user_id).select_related(
        'posted_by').prefetch_related(
        'react_set').annotate(reaction_count=Count('react__reaction')
                              ).order_by('posted_by')[offset:limit + offset]

    comment_queryset = Comment.objects.select_related(
        'commented_by', 'post').filter(commented_by_id=user_id
                                       ).prefetch_related(
        'comment_set', 'react_set',
        'comment_set__commented_by',
        'comment_set__react_set').annotate(
        reaction_count=Count('react__reaction')
    )

    list_of_posts = []
    for post in post_queryset:
        post_dict = {}
        post_dict['post_id'] = post.id
        post_dict['posted_by'] = {'name': post.posted_by.name,
                                  'user_id': post.posted_by.id,
                                  'profile_pic': post.posted_by.profile_pic
                                  }

        post_dict['posted_at'] = post.posted_at
        post_dict['post_content'] = post.content
        list_of_reaction_on_post = []

        for reaction_obj in post.react_set.all():
            list_of_reaction_on_post.append(reaction_obj.reaction)

        post_dict['reactions'] = {
            'count': post.reaction_count,
            'type': list(set(list_of_reaction_on_post))
        }

        list_of_posts = []
        for post in post_queryset:
            post_dict = {
                'post_id': post.id,
                'posted_by': {'name': post.posted_by.name,
                              'user_id': post.posted_by.id,
                              'profile_pic': post.posted_by.profile_pic
                              },
                'posted_at': post.posted_at,
                'post_content': post.content}
            list_of_reaction_on_post = []

            for reaction_obj in post.react_set.all():
                list_of_reaction_on_post.append(reaction_obj.reaction)

            post_dict['reactions'] = {
                'count': post.reaction_count,
                'type': list(set(list_of_reaction_on_post))
            }

            list_of_comments = []
            for comment in comment_queryset:
                comment_dict = {
                    'comment_id': comment.id,
                    'commenter': {'user_id': comment.commented_by.id,
                                  'name': comment.commented_by.name,
                                  'profile_pic':
                                      comment.commented_by.profile_pic
                                  },
                    'commented_at': comment.commented_at,
                    'comment_content': comment.content}

                list_of_reaction_on_comment = []
                for reaction_obj in comment.react_set.all():
                    list_of_reaction_on_comment.append(reaction_obj.reaction)
                comment_dict['reactions'] = {
                    'count': comment.reaction_count,
                    'type': list(set(list_of_reaction_on_comment))
                }

                list_of_replies = []
                reply_objects = comment.comment_set.all()
                for reply in reply_objects:
                    reply_dict = {
                        'reply_id': reply.id,
                        'commenter': {'user_id': reply.commented_by.id,
                                      'name': reply.commented_by.name,
                                      'profile_pic':
                                          reply.commented_by.profile_pic
                                      },
                        'commented_at': reply.commented_at,
                        'comment_content': reply.content}

                    list_of_reaction_on_reply = []
                    for reaction_obj in reply.react_set.all():
                        list_of_reaction_on_reply.append(reaction_obj.reaction)
                    list_of_replies.append(reply_dict)

                list_of_comments.append(comment_dict)
                comment_dict['replies'] = list_of_replies

            post_dict['comments'] = list_of_comments
            list_of_posts.append(post_dict)

        return list_of_posts

    return list_of_posts[offset:limit + offset]


'''Input:  get_group_feed(3,16,0,2)

Output: [{'post_id': 27,
  'posted_by': {'name': 'user 3', 'user_id': 3, 'profile_pic': '3rd'},
  'posted_at': datetime.datetime(2023, 2, 17, 5, 43, 13, 686502, tzinfo=<UTC>),
  'post_content': '1stpost',
  'reactions': {'count': 2, 'type': ['LIT', 'WOW']},
  'comments': [{'comment_id': 13,
    'commenter': {'user_id': 3, 'name': 'user 3', 'profile_pic': '3rd'},
    'commented_at': datetime.datetime(2023, 2, 17, 5, 52, 31, 580644, 
    tzinfo=<UTC>),
    'comment_content': 'very nice',
    'reactions': {'count': 0, 'type': []},
    'replies': [{'reply_id': 17,
      'commenter': {'user_id': 4, 'name': 'user', 'profile_pic': 'dolo'},
      'commented_at': datetime.datetime(2023, 2, 17, 5, 53, 55, 19636, 
      tzinfo=<UTC>),
      'comment_content': 'thanks'}]},
   {'comment_id': 16,
    'commenter': {'user_id': 3, 'name': 'user 3', 'profile_pic': '3rd'},
    'commented_at': datetime.datetime(2023, 2, 17, 5, 53, 16, 799520, 
    tzinfo=<UTC>),
    'comment_content': 'aaag laga di',
    'reactions': {'count': 0, 'type': []},
    'replies': []}]},
 {'post_id': 28,
  'posted_by': {'name': 'user 3', 'user_id': 3, 'profile_pic': '3rd'},
  'posted_at': datetime.datetime(2023, 2, 17, 5, 43, 24, 691962, tzinfo=<UTC>),
  'post_content': '2ndpost',
  'reactions': {'count': 2, 'type': ['LIT', 'WOW']},
  'comments': [{'comment_id': 13,
    'commenter': {'user_id': 3, 'name': 'user 3', 'profile_pic': '3rd'},
    'commented_at': datetime.datetime(2023, 2, 17, 5, 52, 31, 580644, 
    tzinfo=<UTC>),
    'comment_content': 'very nice',
    'reactions': {'count': 0, 'type': []},
    'replies': [{'reply_id': 17,
      'commenter': {'user_id': 4, 'name': 'user', 'profile_pic': 'dolo'},
      'commented_at': datetime.datetime(2023, 2, 17, 5, 53, 55, 19636, 
      tzinfo=<UTC>),
      'comment_content': 'thanks'}]},
   {'comment_id': 16,
    'commenter': {'user_id': 3, 'name': 'user 3', 'profile_pic': '3rd'},
    'commented_at': datetime.datetime(2023, 2, 17, 5, 53, 16, 799520, 
    tzinfo=<UTC>),
    'comment_content': 'aaag laga di',
    'reactions': {'count': 0, 'type': []},
    'replies': []}]}]

'''


# Task 8

def get_posts_with_more_comments_than_reactions() -> List[int]:
    post_ids = Post.objects.prefetch_related('comment_set',
                                             'react_set').values('id'
                                                                 ).annotate(
        comment_count=Count('comment__id'),
        react_count=Count('react__id')
    ).annotate(diff=F('comment_count') - F('react_count')).filter(
        diff__gt=0).values_list(
        'id', flat=True)

    return list(post_ids)


'''Output: post [11]'''


# Task 10

def get_silent_group_members(group_id: int) -> List[int]:
    validate_group_id(group_id)

    group_members = list(
        Group.objects.filter(id=group_id).values_list('members', flat=True))

    users_who_posted_in_group = list(Post.objects.filter(group_id=group_id
                                                         ).values_list(
        'posted_by', flat=True).distinct())

    users_who_not_posted_in_group = [group_member
                                     for group_member in group_members
                                     if
                                     group_member not in users_who_posted_in_group]

    return users_who_not_posted_in_group


'''Input: group_id=16
   Output:  [1, 8] '''


# Task 11
def get_posts_with_more_comments_excluding_replies_than_reactions() -> List[
    int]:
    post_ids = Post.objects.prefetch_related('comment_set',
                                             'react_set').values('id').filter(
        comment__parent_comment_id=None).annotate(
        comment_count=Count('comment__id'),
        react_count=Count('react__id')
    ).annotate(diff=F('comment_count') - F('react_count')).filter(
        diff__gt=0).values_list(
        'id', flat=True)

    return list(post_ids)


'''Output: List_of_post_ids= [11] '''
