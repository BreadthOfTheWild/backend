from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pusher import Pusher
from django.http import JsonResponse
from decouple import config
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
import json
from .models import *


# instantiate pusher
pusher = Pusher(
    app_id=config('PUSHER_APP_ID'), 
    key=config('PUSHER_KEY'), 
    secret=config('PUSHER_SECRET'), 
    cluster=config('PUSHER_CLUSTER')
    )

@csrf_exempt
@api_view(["GET"])
def initialize(request):
    print ("Init called...", request)     
    user = request.user
    player = user.player
    player_id = player.id
    uuid = player.uuid
    room = player.room()
    players = room.playerNames(player_id)
    return JsonResponse({'uuid': uuid, 'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players}, safe=True)

@csrf_exempt
@api_view(["GET"])
def reset(request):
    user = request.user
    player = user.player
    player_id = player.id
    uuid = player.uuid
    # this resets the player
    player.reset()
    room = player.room()
    players = room.playerNames(player_id)
    return JsonResponse({'uuid': uuid, 'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players}, safe=True)


@csrf_exempt
@api_view(["POST"])
def move(request):
    print ("Move called...")
    dirs={"n": "north", "s": "south", "e": "east", "w": "west"}
    reverse_dirs = {"n": "south", "s": "north", "e": "west", "w": "east"}
    player = request.user.player
    player_id = player.id
    player_uuid = player.uuid
    data = json.loads(request.body)
    direction = data['direction']
    room = player.room()
    print ("Data = ", data, " Player = ", player)
    nextRoomID = None
    if direction == "n":
        nextRoomID = room.n_to
    elif direction == "s":
        nextRoomID = room.s_to
    elif direction == "e":
        nextRoomID = room.e_to
    elif direction == "w":
        nextRoomID = room.w_to

    print ("Next room id ", nextRoomID)  
    if nextRoomID is not None and nextRoomID > 0:
        nextRoom = Room.objects.get(id=nextRoomID)
        player.currentRoom=nextRoomID
        player.save()
        players = nextRoom.playerNames(player_id)
        currentPlayerUUIDs = room.playerUUIDs(player_id)
        nextPlayerUUIDs = nextRoom.playerUUIDs(player_id)
        print ("DONE")  
        # for p_uuid in currentPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has walked {dirs[direction]}.'})
        # for p_uuid in nextPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has entered from the {reverse_dirs[direction]}.'})
        
        return JsonResponse({'name':player.user.username, 'title':nextRoom.title, 'description':nextRoom.description, 'players':players, 'error_msg':""}, safe=True)
    else:
        players = room.playerNames(player_id)
        return JsonResponse(
            {'name':player.user.username, 
            'title':room.title, 
            'description':room.description,
            'players':players, 
            'error_msg':"You cannot move that way."}, 
         safe=True)



# def move(request):
#     # pass in the id of the room we are moving to
#     # 'room_id': id
#     # dirs={"n": "north", "s": "south", "e": "east", "w": "west"}
#     # reverse_dirs = {"n": "south", "s": "north", "e": "west", "w": "east"}
#     # player = request.user.player
#     # player_id = player.id
#     # player_uuid = player.uuid
#     # data = json.loads(request.body)
#     # direction = data['direction']
#     # room = player.room()
#     # nextRoomID = None
#     # if direction == "n":
#     #     nextRoomID = room.n_to
#     # elif direction == "s":
#     #     nextRoomID = room.s_to
#     # elif direction == "e":
#     #     nextRoomID = room.e_to
#     # elif direction == "w":
#     #     nextRoomID = room.w_to
#     # if nextRoomID is not None and nextRoomID > 0:
#     #     nextRoom = Room.objects.get(id=nextRoomID)
#     #     player.currentRoom=nextRoomID
#     #     player.save()
#     #     players = nextRoom.playerNames(player_id)
#     #     currentPlayerUUIDs = room.playerUUIDs(player_id)
#     #     nextPlayerUUIDs = nextRoom.playerUUIDs(player_id)
#     #     # for p_uuid in currentPlayerUUIDs:
#     #     #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has walked {dirs[direction]}.'})
#     #     # for p_uuid in nextPlayerUUIDs:
#     #     #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has entered from the {reverse_dirs[direction]}.'})
#     #     return JsonResponse({'name':player.user.username, 'title':nextRoom.title, 'description':nextRoom.description, 'players':players, 'error_msg':""}, safe=True)
#     # else:
#     #     players = room.playerNames(player_id)
#     #     return JsonResponse({'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players, 'error_msg':"You cannot move that way."}, safe=True)
#     player = request.user.player
#     data = json.loads(request.body)
#     player.currentRoom = int(data['room_id'])
#     room = player.room()
#     current_room = {
#         'id': room.id, 
#         'title': room.title, 
#         'description': room.description,
#         'n_to': room.n_to,
#         's_to': room.s_to,
#         'e_to': room.e_to,
#         'w_to': room.w_to,
#         'locx': room.locx,
#         'locy': room.locy,
#         'players': room.playerNames(player.id)
#     }
#     return JsonResponse({'id': player.id, 'name': player.user.username, 'uuid': player.uuid, 'room': current_room}, safe=True)

















@csrf_exempt
@api_view(["GET"])
def getRooms(request):
    print ("Get rooms called...")
    #Get all rooms from DB

    #And return in response
    roomTitles = []
    print ("Rooms : ",Room.objects.all())
    for room in Room.objects.all():
        print(room.title)
        roomTitles.append(room.title)
        print(roomTitles)

    return JsonResponse({'rooms' : roomTitles}, safe=True)

@csrf_exempt
@api_view(["POST"])
def say(request):
    # IMPLEMENT
    player = request.user.player
    # player_id = player.id
    # player_uuid = player.uuid
    data = json.loads(request.body)
    chat = data['chat']
    pusher.trigger(f'djungle-app-channel', u'my-event', {u'chat': f'{chat}' f'{player.user.username}'})
    return JsonResponse({'message':f'Checking that chat message: *** {chat} *** was sent'}, safe=True )
    # maybe add relevant status?