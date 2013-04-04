import collections

AccessToken = collections.namedtuple('AccessToken', ['access_token', 'expires_in'])


class LinkedInRecipient(object):
    def __init__(self, member_id, email, first_name, last_name):
        assert member_id or email, 'Either member ID or email must be given'
        if member_id:
            self.member_id = str(member_id)
        else:
            self.member_id = None
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

    @property
    def json(self):
        result = {'person': None}
        if self.member_id:
            result['person'] = {'_path': '/people/id=%s' % self.member_id}
        else:
            result['person'] = {'_path': '/people/email=%s' % self.email}

        if self.first_name:
            result['person']['first-name'] = self.first_name

        if self.last_name:
            result['person']['last-name'] = self.last_name

        return result


class LinkedInInvitation(object):
    def __init__(self, subject, body, recipients, connect_type, auth_name=None,
                 auth_value=None):
        self.subject = subject
        self.body = body
        self.recipients = recipients
        self.connect_type = connect_type
        self.auth_name = auth_name
        self.auth_value = auth_value

    @property
    def json(self):
        result = {
            'recipients': {
                'values': []
            },
            'subject': self.subject,
            'body': self.body,
            'item-content': {
                'invitation-request': {
                    'connect-type': self.connect_type
                }
            }
        }
        for recipient in self.recipients:
            result['recipients']['values'].append(recipient.json)

        if self.auth_name and self.auth_value:
            auth = {'name': self.auth_name, 'value': self.auth_value}
            result['item-content']['invitation-request']['authorization'] = auth

        return result
