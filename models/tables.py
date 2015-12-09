from datetime import datetime

db.define_table('user_messages',
                Field('userfrom', 'integer'),
                Field('userto', 'integer'),
                Field('msg'),
                Field('msg_time', 'datetime', default = datetime.utcnow()),
                Field('img', 'integer', default=None)
                )

db.define_table('images',
                Field('name'),
                Field('image', 'upload'),
                Field('uploader', 'integer', default = auth.user_id),
                format = '%(uploader)s/%(name)s'
                )

db.user_messages.userfrom.readable = db.user_messages.userfrom.writable = False
db.user_messages.userto.readable = db.user_messages.userto.writable = False
db.images.uploader.readable = db.images.uploader.writable = False
