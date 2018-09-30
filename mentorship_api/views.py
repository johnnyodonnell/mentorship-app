from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User

from mentorship_profile.models import Profile, Mentor, Mentee
from mentorship_api.serializers import UserSerializer, ProfileSerializer, \
        MentorSerializer, MenteeSerializer


# https://stackoverflow.com/questions/405489/python-update-object-from-dictionary
def assign_dict(obj, updateDict):
    for key, value in updateDict.items():
        setattr(obj, key, value)


class UserGeneral(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        response = {}

        user = request.user
        userSerializer = UserSerializer(user)
        response["user"] = userSerializer.data

        profile = Profile.objects.get(pk=user.profile.id)
        profileSerializer = ProfileSerializer(profile)
        response["profile"] = profileSerializer.data

        if (profile.is_mentor()):
            mentor = Mentor.objects.get(pk=user.profile.mentor.id)
            mentorSerializer = MentorSerializer(mentor)
            response["mentor"] = mentorSerializer.data

        if (profile.is_mentee()):
            mentee = Mentee.objects.get(pk=user.profile.mentee.id)
            menteeSerializer = MenteeSerializer(mentee)
            response["mentee"] = menteeSerializer.data

        return Response(response)

    def post(self, request, format=None):
        jsonData = request.data

        userData = jsonData.get("user", None)
        profileData = jsonData.get("profile", None)
        mentorData = jsonData.get("mentor", None)
        menteeData = jsonData.get("mentee", None)

        userSerializer = UserSerializer(data=userData)
        profileSerializer = ProfileSerializer(data=profileData)
        mentorSerializer = None
        menteeSerializer = None

        if mentorData:
            mentorSerializer = MentorSerializer(data=mentorData)

        if menteeData:
            menteeSerializer = MenteeSerializer(data=menteeData)

        errors = None

        if not (userSerializer.is_valid()):
            errors = errors or {}
            errors["user"] = userSerializer.errors

        if not (profileSerializer.is_valid()):
            errors = errors or {}
            errors["profile"] = profileSerializer.errors

        if mentorSerializer and (not mentorSerializer.is_valid()):
            errors = errors or {}
            errors["mentor"] = mentorSerializer.errors

        if menteeSerializer and (not menteeSerializer.is_valid()):
            errors = errors or {}
            errors["mentee"] = menteeSerializer.errors

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = userSerializer.save()

            profileSerializer.instance = user.profile
            profile = profileSerializer.save()

            if mentorSerializer:
                mentorSerializer.save(profile=profile)

            if mentorSerializer:
                menteeSerializer.save(profile=profile)

            response = {}
            response["user_id"] = userSerializer.data["id"]
            response["profile_id"] = profileSerializer.data["id"]

            if mentorSerializer:
                response["mentor_id"] = mentorSerializer.data["id"]

            if menteeSerializer:
                response["mentee_id"] = menteeSerializer.data["id"]

            return Response(response, status=status.HTTP_201_CREATED)


class UserDetail(APIView):
    def post(self, request, user_id, format=None):
        jsonData = request.data

        userData = jsonData.get("user", None)
        profileData = jsonData.get("profile", None)
        mentorData = jsonData.get("mentor", None)
        menteeData = jsonData.get("mentee", None)

        user = request.user
        profile = Profile.objects.get(pk=user.profile.id)
        mentor = None
        mentee = None

        if (profile.is_mentor()):
            mentor = Mentor.objects.get(pk=user.profile.mentor.id)

        if (profile.is_mentee()):
            mentee = Mentee.objects.get(pk=user.profile.mentee.id)

        if userData:
            assign_dict(user, userData)
            user.save()

        if profileData:
            assign_dict(profile, profileData)
            profile.save()

        if mentor and mentorData:
            assign_dict(mentor, mentorData)
            mentor.save()

        if mentee and menteeData:
            assign_dict(mentee, menteeData)
            mentee.save()

        return Response(status=status.HTTP_200_OK)
