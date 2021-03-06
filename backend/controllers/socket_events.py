from wsgi import socket_io
from datetime import datetime
from flask import request
from models.setting import update_room
from flask_socketio import emit, join_room, leave_room
from models.participate import join_participate, leave_participate, query_all_participate, query_participate_request_sid
from controllers.celery_tasks import pull_participate_after_disconnect, record_chat_log, record_draw_log
import os


@socket_io.on('connect')
def client_connect():
  print('connect', request.sid)


@socket_io.on('join-room')
def new_join_room(join_data):
  room_uuid = join_data['roomUuid']
  join_message = {
      'talkerName': join_data['participate']['userName'],
      'talkerUuid': join_data['participate']['userUuid'],
      'text': f" ({join_data['participate']['role']}, {join_data['participate']['mode']}) has joined this room."
  }
  if join_data['action'] == 'join':
    current_all_participate = query_all_participate(room_uuid)
    if len(current_all_participate['participates']) <= 0:
      update_room({'room_uuid': room_uuid, 'is_active': True, 'last_activity': datetime.utcnow()})
    join_participate({'room_uuid': room_uuid, 'participate': {
                     **join_data['participate'], 'room_uuid': room_uuid, 'request_sid': request.sid}})

  join_room(room_uuid)
  record_chat_log(room_uuid, join_message)
  emit('join-room', join_message, to=room_uuid)


@socket_io.on('send-chat')
def chatting(chatting_data):
  room_uuid = chatting_data.pop('roomUuid')
  record_chat_log(room_uuid, chatting_data)
  emit('receive-chat', chatting_data, to=room_uuid)


@socket_io.on('send-draw')
def drawing(drawing_data):
  room_uuid = drawing_data['roomUuid']
  emit('receive-draw', drawing_data, to=room_uuid)


@socket_io.on('save-draw')
def save_drawing(drawing_data):
  room_uuid = drawing_data['roomUuid']
  canvas_snap_shot = drawing_data['canvasSnapShot']
  record_draw_log(room_uuid, canvas_snap_shot)


@socket_io.on('leave-room')
def old_leave_room(leave_data):
  room_uuid = leave_data['roomUuid']
  leave_message = {
      'talkerName': leave_data['participate']['userName'],
      'talkerUuid': leave_data['participate']['userUuid'],
      'text': f"({leave_data['participate']['role']}, {leave_data['participate']['mode']}) has left this room."
  }
  if leave_data['action'] == 'leave':
    current_all_participate = query_all_participate(room_uuid)
    if len(current_all_participate['participates']) - 1 <= 0:
      active = True if (room_uuid == os.getenv('ACTIVE_ROOM_DEV') or room_uuid == os.getenv('ACTIVE_ROOM_ONE')
                        or room_uuid == os.getenv('ACTIVE_ROOM_TWO')) else False
      update_room({'room_uuid': room_uuid, 'is_active': active, 'last_activity': datetime.utcnow()})
    leave_participate({'room_uuid': room_uuid, 'participate': {
                      **leave_data['participate'], 'room_uuid': room_uuid, 'request_sid': request.sid}})
  leave_room(room_uuid)
  record_chat_log(room_uuid, leave_message)
  emit('leave-room', leave_message, to=room_uuid)


@socket_io.on('disconnect')
def client_disconnect():
  try:
    participate = query_participate_request_sid(request.sid)
    if participate:
      leave_message = {
          'talkerName': participate['userName'],
          'talkerUuid': participate['userUuid'],
          'text': f"({participate['role']}, {participate['mode']}) has left this room."
      }
      record_chat_log(participate['room_uuid'], leave_message)
      emit('receive-chat', leave_message, to=participate['room_uuid'])
      pull_participate_after_disconnect(participate)
      print(request.sid, 'client disconnect!')
  except:
    return
