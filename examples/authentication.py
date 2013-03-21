from linkedin.linkedin import (LinkedInAuthentication, LinkedInApplication,
                               PERMISSIONS)

from linkedin.models import AccessToken
if __name__ == '__main__':
    API_KEY = 'wFNJekVpDCJtRPFX812pQsJee-gt0zO4X5XmG6wcfSOSlLocxodAXNMbl0_hw3Vl'
    API_SECRET = 'daJDa6_8UcnGMw1yuq9TjoO_PMKukXMo8vEMo7Qv5J-G3SPgrAV0FqFCd0TNjQyG'
    RETURN_URL = 'http://localhost:8000'
    authentication = LinkedInAuthentication(API_KEY, API_SECRET, RETURN_URL,
                                            PERMISSIONS.enums.values())
    print authentication.authorization_url
    application = LinkedInApplication(authentication)

    authentication.token = AccessToken(access_token=u'AQUXcfwpaE1BGsgDaqGAl2Mrg3R_f73avFuU5NsZplotodGMpuni0Sk6aZpofCKLCuXN1G18mlNotA2Iv67IhzHnqwzly3Q0yBBHcocnUQgdBdYJ1E35s8I6efF8EQhXnCe46Evck6dJ7KWh5ttLFSyxuSJexRkJDkMeelmi2wMV4WfcjMw', expires_in=5099296)
