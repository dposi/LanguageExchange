from datetime import datetime

db.define_table('messages',
                Field('userfrom', db.auth_user),
                Field('userto', db.auth_user),
                Field('msg'),
                Field('msg_time', 'datetime', default = datetime.utcnow())
                )
