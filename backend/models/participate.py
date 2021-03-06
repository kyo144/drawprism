from models.db_mongo_atlas import db


def query_all_participate(room_uuid):
  return db.room_participates.find_one({'room_uuid': room_uuid}, {'_id': False})


def query_participate_request_sid(request_sid):
  try:
    cursor = db.room_participates.find({'participates': {'$elemMatch': {'request_sid': {'$eq': request_sid}}}})
    for result in cursor:
      for participate in result['participates']:
        if participate['request_sid'] == request_sid:
          return participate
  except:
    return None


def join_participate(join_data):
  db.room_participates.update_one(
      {'room_uuid': join_data['room_uuid']},
      {'$push': {'participates': join_data['participate']}}
  )


def leave_participate(leave_data):
  db.room_participates.update_one(
      {'room_uuid': leave_data['room_uuid']},
      {'$pull': {'participates': leave_data['participate']}}
  )
