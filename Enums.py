from enum import Enum


class ReactionEnum(Enum):
    WOW = 'WOW',
    LIT = 'LIT',
    LOVE = 'LOVE',
    HAHA = ' HAHA',
    THUMBS_UP = 'THUMBS_UP',
    THUMBS_DOWN = 'THUMBS_DOWN',
    ANGRY = 'ANGRY',
    SAD = 'SAD'

    @staticmethod
    def list_of_reaction_enum():
        list_of_choices = [ReactionEnum.WOW.value,
                           ReactionEnum.LIT.value,
                           ReactionEnum.LOVE.value,
                           ReactionEnum.HAHA.value,
                           ReactionEnum.THUMBS_UP.value,
                           ReactionEnum.THUMBS_DOWN.value,
                           ReactionEnum.ANGRY.value,
                           ReactionEnum.SAD.value]
        choice_list=[]
        for choice in list_of_choices:
            for i in choice:
                choice_list.append(i)
        return choice_list
