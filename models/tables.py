from datetime import datetime

db.define_table('userinfo',
                Field('screenname', requires=IS_NOT_EMPTY()),
                Field('fluent', 'list:string'),
                Field('learn', 'list:string')
                )

db.define_table('messages',
                Field('userfrom', 'reference userinfo'),
                Field('userto', 'reference userinfo'),
                Field('msg'),
                Field('msg_time', 'datetime', default = datetime.utcnow())
                )
