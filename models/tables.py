from datetime import datetime

db.define_table('user_messages',
                Field('userfrom', 'integer'),
                Field('userto', 'integer'),
                Field('msg'),
                Field('msg_time', 'datetime', default = datetime.utcnow())
                )