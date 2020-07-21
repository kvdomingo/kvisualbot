import json

from sqlalchemy import exc
from sqlalchemy import func

from . import Session
from .models import *


def textualize(obj) -> str:
    message = ""
    for k, v in obj.to_dict().items():
        message += f"\n`{k}`: {v}"
    return message


class GroupApi:
    name = 'group'

    def get(self, name: str = None) -> str:
        sess = Session()
        if name is None or name == 'all':
            query = sess.query(Group).order_by(Group.name).all()
            message = f"Here are all the {self.name}s I currently support:"
            for obj in query:
                message += "\n"
                message += textualize(obj)
        else:
            obj = sess.query(Group).filter(Group.name == name).first()
            if obj:
                message = f"""I have records of a {self.name} matching your query "`{name}`":\n"""
                message += textualize(obj)
            else:
                message = f"""Sorry, I couldn't find a record of a {self.name} matching your query "`{name}`" :cry:"""
        sess.close()
        return message

    def create(
            self,
            name: str,
            vlive_channel_code: str = None,
            vlive_channel_seq: int = None,
            vlive_last_seq: int = None
    ) -> str:
        fields = {k: v for k, v in list(locals().items())[1:]}
        sess = Session()
        g_id = sess.query(func.max(Group.id)).first()[0] + 1
        fields['name'] = fields['name'].lower()
        fields['id'] = g_id
        obj = Group(**fields)
        sess.add(obj)
        try:
            sess.commit()
            g_id = obj.id
            message = f"I've created {self.name} **{obj.name}** with the following details:\n"
            message += textualize(obj)
            print(f"Created {self.name} {g_id}")
        except exc.SQLAlchemyError as e:
            message = f"Sorry, I couldn't create the {self.name}. Please try again later!"
            print(e)
        sess.close()
        return message

    def update(self, old_name: str, new_name: str) -> str:
        sess = Session()
        obj = sess.query(Group).filter(Group.name == old_name.lower()).first()
        obj.name = new_name.lower()
        try:
            sess.commit()
            qid = obj.id
            message = f"I've updated {self.name} **{obj.name}** with the following details:\n"
            message += textualize(obj)
            print(f"Updated {self.name} {qid}")
        except exc.SQLAlchemyError as e:
            message = f"Sorry, I couldn't update the {self.name}. Please try again later!"
            print(e)
        sess.close()
        return message


class MemberApi:
    name = 'member'

    def get(self, group: str, name: str = None) -> str:
        sess = Session()
        if name == 'all' or name is None:
            queryset = sess.query(Member).filter(Member.group.has(name=group)).all()
            message = f"Here are all the {self.name}s of the group {group.upper()}:"
            for obj in queryset:
                message += f"\n{textualize(obj)}"
        else:
            obj = sess.query(Member).filter(Member.group.has(name=group)).filter(Member.stage_name == name).first()
            if obj:
                message = f"""Here are the details of "`{name}`" of {group.upper()}:\n"""
                message += textualize(obj)
            else:
                message = f"""Sorry, I couldn't find a member with the name or alias of "`{name}`" """
        sess.close()
        return message

    def create(self, group: str, stage_name: str, family_name: str, given_name: str) -> str:
        fields = {k: v for k, v in list(locals().items())[1:]}
        sess = Session()
        m_id = sess.query(func.max(Member.id)).first()[0] + 1
        group_id = sess.query(Group).filter(Group.name == fields['group']).first().id
        fields['id'] = m_id
        fields['group_id'] = group_id
        del fields['group']
        obj = Member(**fields)
        try:
            sess.add(obj)
            sess.commit()
            m_id = obj.id
            message = f"I've created {self.name} **{obj.stage_name}** with the following details:\n"
            message += textualize(obj)
            print(f"Created {self.name} {m_id}")
        except exc.SQLAlchemyError as e:
            message = f"Sorry, I couldn't create the {self.name}. Please try again later!"
            print(e)
        sess.close()
        return message


class AccountApi:
    name = 'twitter account'

    def get(self, group: str, member: str) -> str:
        sess = Session()
        accounts = (
            sess.query(Member)
                .filter(Member.group.has(name=group))
                .filter(Member.stage_name == member)
                .first()
                .twitter_accounts
        )
        message = f"Here are all the {self.name}s for {member}:"
        for obj in accounts:
            message += f"\n{textualize(obj)}"
        sess.close()
        return message

    def create(self, group: str, member: str, account_name: str) -> str:
        fields = {k: v for k, v in list(locals().items())[1:]}
        sess = Session()
        a_id = sess.query(func.max(TwitterAccount.id)).first()[0] + 1
        member_id = sess.query(Member).filter(Member.group.has(name=fields['group'])).filter(
            Member.stage_name == fields['member']).first().id
        fields['id'] = a_id
        fields['member_id'] = member_id
        del fields['member'], fields['group']
        obj = TwitterAccount(**fields)
        try:
            sess.add(obj)
            sess.commit()
            a_id = obj.id
            message = f"I've created {self.name} @{obj.account_name} for {member} with the following details:\n"
            message += textualize(obj)
            print(f"Created twitter account {a_id}")
        except exc.SQLAlchemyError as e:
            message = f"Sorry, I couldn't create the {self.name}. Please try again later!"
            print(e)
        sess.close()
        return message

    def update(self, group: str, member: str, old_account: str, new_account: str) -> str:
        fields = {k: v for k, v in list(locals().items())[1:]}
        sess = Session()
        obj = (
            sess.query(TwitterAccount)
                .join(TwitterAccount.member)
                .filter(Member.group.has(name=fields['group']))
                .filter(Member.stage_name == fields['member'])
                .filter(TwitterAccount.account_name == fields['old_account'])
                .first()
        )
        obj.account_name = fields['new_account']
        try:
            sess.commit()
            m_id = obj.id
            message = f"Updated {self.name} @{old_account} with the following details:\n"
            message += textualize(obj)
            print(f"Updated twitter account {m_id}")
        except exc.SQLAlchemyError as e:
            message = f"Sorry, I couldn't update the {self.name}. Please try again later!"
            print(e)
        sess.close()
        return message


class AliasApi:
    name = 'alias'

    def get(self, group: str, member: str) -> str:
        sess = Session()
        query = (
            sess.query(Alias)
                .join(Alias.member)
                .filter(Member.group.has(name=group))
                .filter(Member.stage_name == member)
                .all()
        )
        message = f"Here are all the {self.name}es for {member}:"
        for obj in query:
            message += f"\n{textualize(obj)}"
        sess.close()
        return message

    def create(self, group: str, member: str, alias: str) -> str:
        fields = {k: v for k, v in list(locals().items())[1:]}
        sess = Session()
        a_id = sess.query(func.max(Alias.id)).first()[0] + 1
        m_id = (
            sess.query(Member)
                .filter(Member.group.has(name=fields['group']))
                .filter(Member.stage_name == fields['member'])
                .first()
                .id
        )
        fields['member_id'] = m_id
        fields['id'] = a_id
        del fields['member'], fields['group']
        obj = Alias(**fields)
        try:
            sess.add(obj)
            sess.commit()
            a_id = obj.id
            message = f"""I've created the {self.name} "{alias}" for {member} with the following details:\n"""
            message += textualize(obj)
            print(f"Created alias {a_id}")
        except exc.SQLAlchemyError as e:
            message = f"Sorry, I couldn't create the {self.name}. Please try again later!"
            print(e)
        sess.close()
        return message


class TwitterChannelApi:
    name = "twitter-subscribed channel"

    def create(self, channel_id: int, group: str) -> str:
        sess = Session()
        obj = (
            sess.query(TwitterChannel)
                .filter(TwitterChannel.channel_id == channel_id)
                .filter(TwitterChannel.group.has(name=group.lower()))
                .first()
        )
        if obj:
            message = f"This channel is already subscribed to hourly {obj.group.name.upper()} updates!"
        else:
            g_id = sess.query(Group).filter(Group.name == group.lower()).first().id
            c_id = sess.query(func.max(TwitterChannel.id)).first()[0] + 1
            obj = TwitterChannel(id=c_id, channel_id=channel_id, group_id=g_id)
            try:
                sess.add(obj)
                sess.commit()
                c_id = obj.id
                message = f"This channel has been subscribed to hourly {obj.group.name.upper()} updates with the following details:\n"
                message += textualize(obj)
                print(f"Created twitter channel {c_id}")
            except exc.SQLAlchemyError as e:
                message = f"Sorry, I couldn't subscribe this channel. Please try again later!"
                print(e)
        sess.close()
        return message

    def delete(self, channel_id: int, group: str) -> str:
        sess = Session()
        obj = (
            sess.query(TwitterChannel)
                .filter(TwitterChannel.channel_id == channel_id)
                .filter(TwitterChannel.group.has(name=group.lower()))
                .first()
        )
        if not obj:
            message = f"This channel is not subscribed to hourly {group.upper()} updates!"
        else:
            sess.delete(obj)
            c_id = obj.id
            message = f"This channel has been unsubscribed from {group.upper()} updates"
            print(f"Deleted channel {c_id}")
        sess.close()
        return message


class VliveChannelApi:
    name = "vlive-subscribed channel"

    def create(self, channel_id: int, group: str) -> str:
        sess = Session()
        obj = sess.query(VliveChannel).filter(VliveChannel.channel_id == channel_id).first()
        if obj:
            message = f"This channel is already subscribed to {obj.group.name.upper()} notifications!"
        else:
            g_id = sess.query(Group).filter(Group.name == group.lower()).first().id
            c_id = sess.query(func.max(VliveChannel.id)).first()[0] + 1
            obj = VliveChannel(id=c_id, channel_id=channel_id, group_id=g_id)
            try:
                sess.add(obj)
                sess.commit()
                c_id = obj.id
                message = f"This channel has been subscribed to {obj.group.name.upper()} VLIVE alerts with the following details:\n"
                message += textualize(obj)
                print(f"Created channel {c_id}")
            except exc.SQLAlchemyError as e:
                message = f"Sorry, I couldn't subscribe this channel. Please try again later!"
                print(e)
        sess.close()
        return message

    def delete(self, channel_id: int) -> str:
        sess = Session()
        obj = sess.query(VliveChannel).filter(VliveChannel.channel_id == channel_id).first()
        if not obj:
            message = "This channel is not subscribed to any VLIVE notifications!"
        else:
            sess.delete(obj)
            c_id = obj.id
            message = f"This channel has been unsubscribed from {obj.group.name.upper()} VLIVE notifications!"
            print(f"Deleted channel {c_id}")
        sess.close()
        return message
