from django.shortcuts import render
from rest_framework import generics
from .serializers import RoomSerializer, CreateRoomSerializer
from .models import Room
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
class RoomView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class GetRoom(APIView):
    serializer_class = RoomSerializer
    ## lookup_url_kwarg is the name of the parameter in the url
    lookup_url_kwarg = 'code'

    def get(self, request, format=None):
        ## request.GET.get() gets the value of the parameter in the url
        code = request.GET.get(self.lookup_url_kwarg)

        ## if the code is not None, then we filter the room by the code
        if code != None:
            ## filter returns a list of objects
            room = Room.objects.filter(code=code)
            ## if the room exists, then we return the room
            if len(room) > 0:
                ## data is a dictionary of the room
                data = RoomSerializer(room[0]).data
                ## is_host is a boolean that is true if the session key is the same as the host 
                data['is_host'] = self.request.session.session_key == room[0].host

                return Response(data, status=status.HTTP_200_OK)

            return Response({'Room Not Found': 'Invalid Room Code'}, status=status.HTTP_404_NOT_FOUND)


class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer

    def post(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            host = self.request.session.session_key
            queryset = Room.objects.filter(host=host)
            if queryset.exists():
                room = queryset[0]
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip
                room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
                return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
            else:
                room = Room(host=host, guest_can_pause=guest_can_pause,
                            votes_to_skip=votes_to_skip)
                room.save()
                return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)

        return Response({'Bad Request': 'Invalid data...'}, status=status.HTTP_400_BAD_REQUEST)