class InvalidUserException(Exception):
    pass


class InvalidPostException(Exception):
    pass


class InvalidCommentContent(Exception):
    pass


class InvalidReplyContent(Exception):
    pass


class InvalidReactionTypeException(Exception):
    pass


class UserCannotDeletePostException(Exception):
    pass


class InvalidGroupNameException(Exception):
    pass


class InvalidMemberException(Exception):
    pass


class InvalidGroupException(Exception):
    pass


class UserNotInGroupException(Exception):
    pass


class UserIsNotAdminException(Exception):
    pass


class InvalidOffSetValueException(Exception):
    pass


class InvalidLimitValueException(Exception):
    pass


'''
def checking_post_content:
    try:
        if len(post_content) == 0:
            raise InvalidPostException

    except InvalidPostException:
        print('Invalid Post')'''
