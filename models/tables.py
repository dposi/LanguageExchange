from datetime import datetime

db.define_table('messages',
                Field('userfrom', 'reference auth_user'),
                Field('userto', 'reference auth_user'),
                Field('msg'),
                Field('msg_time', 'datetime', default = datetime.utcnow())
                )
