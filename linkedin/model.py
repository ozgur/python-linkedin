import datetime

from xml.dom import minidom
from xml.sax.saxutils import unescape

class LinkedInModel:
    pass
    def __repr__(self):
        d = {}
        for x,y in self.__dict__.items():
            if (self.__dict__[x]):
                d[x] = y
        return (self.__module__ + "." + self.__class__.__name__ + " " +
                d.__repr__())

class Education(LinkedInModel):
    """
    Class that wraps an education info of a user
    """
    def __init__(self):
        self.id          = None
        self.school_name = None
        self.degree      = None
        self.start_date  = None
        self.end_date    = None
        self.activities  = None
        self.notes       = None
        self.field_of_study = None
        
    @staticmethod
    def create(node):
        """
        <educations total="">
         <education>
          <id>
          <school-name>
          <degree>
          <start-date>
           <year>
          </start-date>
          <end-date>
           <year>
          </end-date>
         </education>
        </educations>
        """
        children = node.getElementsByTagName("education")
        result = []
        for child in children:
            education = Education()
            education.id = education._get_child(child, "id")
            education.activities = education._get_child(child, "activities")
            education.notes = education._get_child(child, "notes")
            education.school_name = education._get_child(child, "school-name")
            education.degree = education._get_child(child, "degree")
            education.field_of_study = education._get_child(child, "field-of-study")
            start_date = child.getElementsByTagName("start-date")
            if start_date:
                start_date = start_date[0]
                try:
                    year = int(education._get_child(start_date, "year"))
                    education.start_date = datetime.date(year, 1, 1)
                    month = int(education._get_child(start_date, "month"))
                    education.start_date = datetime.date(year, month, 1)
                except Exception:
                    pass

            end_date = child.getElementsByTagName("end-date")
            if end_date:
                end_date = end_date[0]
                try:
                    year = int(education._get_child(end_date, "year"))
                    education.end_date = datetime.date(year, 1, 1)
                    month = int(education._get_child(end_date, "month"))
                    education.end_date = datetime.date(year, month, 1)
                except Exception:
                    pass

            result.append(education)            
        return result
    
    def _get_child(self, node, tagName):
        try:
            domNode = node.getElementsByTagName(tagName)[0]
            childNodes = domNode.childNodes
            if childNodes:
                return childNodes[0].nodeValue
            return None
        except:
            return None

class Position(LinkedInModel):
    """
    Class that wraps a business position info of a user
    """
    def __init__(self):
        self.id         = None
        self.title      = None
        self.summary    = None
        self.start_date = None
        self.end_date   = None
        self.company    = None
        

    @staticmethod
    def create(node):
        """
        <positions total='1'>
         <position>
          <id>101526695</id>
          <title>Developer</title>
          <summary></summary>
          <start-date>
          <year>2009</year>
          <month>9</month>
          </start-date>
          <is-current>true</is-current>
          <company>
          <name>Akinon</name>
          </company>
         </position>
        </positions>
        """
        children = node.getElementsByTagName("position")
        result = []
        for child in children:
            position = Position()
            position.id = position._get_child(child, "id")
            position.title = position._get_child(child, "title")
            position.summary = position._get_child(child, "summary")
            company = child.getElementsByTagName("company")
            if company:
                company = company[0]
                position.company = position._get_child(company, "name")
            
            start_date = child.getElementsByTagName("start-date")
            if start_date:
                start_date = start_date[0]
                try:
                    year = int(position._get_child(start_date, "year"))
                    position.start_date = datetime.date(year, 1, 1)
                    month = int(position._get_child(start_date, "month"))
                    position.start_date = datetime.date(year, month, 1)
                except Exception:
                    pass

            end_date = child.getElementsByTagName("end-date")
            if end_date:
                end_date = end_date[0]
                try:
                    year = int(position._get_child(end_date, "year"))
                    position.end_date = datetime.date(year, 1, 1)
                    month = int(position._get_child(end_date, "month"))
                    position.end_date = datetime.date(year, month, 1)
                except Exception:
                    pass

            result.append(position)

        return result
            

    def _get_child(self, node, tagName):
        try:
            domNode = node.getElementsByTagName(tagName)[0]
            childNodes = domNode.childNodes
            if childNodes:
                return childNodes[0].nodeValue
            return None
        except:
            return None
    
class Profile(LinkedInModel):
    """
    Wraps the data which comes from Profile API of LinkedIn.
    For further information, take a look at LinkedIn Profile API.
    """
    def __init__(self):
        self.id          = None
        self.first_name  = None
        self.last_name   = None
        self.location    = None
        self.location_country = None
        self.industry    = None
        self.summary     = None
        self.specialties = None
        self.interests   = None
        self.honors      = None
        self.positions   = []
        self.educations  = []
        self.public_url  = None
        self.private_url = None
        self.picture_url = None
        self.current_status = None
        self.languages   = []
        self.skills      = []
        
    @staticmethod
    def create(xml_string):
        """
        @This method is a static method so it shouldn't be called from an instance.
        
        Parses the given xml string and results in a Profile instance.
        If the given instance is not valid, this method returns NULL.
        """
        try:
            document = minidom.parseString(xml_string)            
            person = document.getElementsByTagName("person")[0]
            profile = Profile()
            profile.id = profile._get_child(person, "id")
            profile.first_name = profile._get_child(person, "first-name")
            profile.last_name = profile._get_child(person, "last-name")
            profile.headline = profile._get_child(person, "headline")
            profile.specialties = profile._get_child(person, "specialties")
            profile.industry = profile._get_child(person, "industry")
            profile.honors = profile._get_child(person, "honors")
            profile.interests = profile._get_child(person, "interests")
            profile.summary = profile._get_child(person, "summary")
            profile.picture_url = profile._unescape(profile._get_child(person, "picture-url"))
            profile.current_status = profile._get_child(person, "current-status")
            profile.public_url = profile._unescape(profile._get_child(person, "public-profile-url"))
            
            # create location
            location = person.getElementsByTagName("location")
            if location:
                location = location[0]
                profile.location = profile._get_child(location, "name")
                country = location.getElementsByTagName('country')[0]
                profile.location_country = profile._get_child(country, "code")

            private_profile = person.getElementsByTagName("site-standard-profile-request")
            if private_profile:
                private_profile = private_profile[0]
                profile.private_url = profile._get_child(private_profile, "url")

            # create skills
            skills = person.getElementsByTagName("skills")
            if skills:
                skills = skills[0]
                children = skills.getElementsByTagName('skill')
                for child in children:
                    if not child.getElementsByTagName('id'):
                        profile.skills.append(profile._get_child(child, 'name'))
                
            # create languages
            languages = person.getElementsByTagName("languages")
            if languages:
                languages = languages[0]
                children = languages.getElementsByTagName('language')
                for child in children:
                    if not child.getElementsByTagName('id'):
                        profile.languages.append(profile._get_child(child, 'name'))

            # create positions
            positions = person.getElementsByTagName("positions")
            if positions:
                positions = positions[0]
                profile.positions = Position.create(positions)

            # create educations
            educations = person.getElementsByTagName("educations")
            if educations:
                educations = educations[0]
                profile.educations = Education.create(educations)
            return profile
        except:
            return None

        return None

    def _unescape(self, url):
        if url:
            return unescape(url)
        return url

    def _get_child(self, node, tagName):
        try:
            if tagName == "summary":
                for n in node.getElementsByTagName(tagName):
                    if n.parentNode.tagName == node.tagName:
                        domNode = n
                        break
            else:
                domNode = node.getElementsByTagName(tagName)[0]

            if domNode.parentNode.tagName == node.tagName:
                childNodes = domNode.childNodes
                if childNodes:
                    return childNodes[0].nodeValue
                return None
            else:
                return None
        except:
            return None