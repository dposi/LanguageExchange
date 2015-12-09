# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################


def index():
    if auth.user_id is not None:
        redirect(URL('default', 'home'))
    return dict()


def descr():
    """
    description of website
    """
    return dict()


@auth.requires_login()
def init_user():
    """
    Initializes a new user's account by creating the necessary records in db.languages
    """
    auth.user = db.auth_user(auth.user_id)
    db.languages.insert(owner_id = auth.user_id, fluent = True)
    db.languages.insert(owner_id = auth.user_id, fluent = False)
    for record in db(db.languages.owner_id == auth.user_id).select():
        if record.fluent == True:
            db(db.auth_user.id == auth.user_id).update(fluent = record)
        else:
            db(db.auth_user.id == auth.user_id).update(learning = record)
    redirect(URL('default', 'reg_lang'))
    return dict()


@auth.requires_login()
@auth.requires_signature()
def load_messages():
    #old shitty way
    """messages_to = db((db.user_messages.userfrom == auth.user_id)&(db.user_messages.userto == request.args(0))).select()
    messages_from = db((db.user_messages.userfrom == request.args(0))&(db.user_messages.userto == auth.user_id)).select()
    messages = messages_to | messages_from
    message_list = messages.as_list()
    message_list.sort(key=lambda message: message['msg_time'])
    d = {m['id']: {'msg_id': m['id'], 'msg': m['msg']} for m in message_list}"""

    #new beautiful way
    messages = db(
        ((db.user_messages.userfrom == auth.user_id)&(db.user_messages.userto == request.args(0))) |
        ((db.user_messages.userfrom == request.args(0))&(db.user_messages.userto == auth.user_id))
    ).select()
    #sorting the messages isnt even necessary because they are displayed in order of id which is always chronological
    d = {m.id: {'msg_id': m.id, 'msg': m.msg, 'sent': m.userfrom == auth.user_id, 'img': db.images(m.img)} for m in messages}
    return response.json(dict(message_dict=d))


@auth.requires_login()
@auth.requires_signature()
def add_message():
    db.user_messages.insert(userfrom = auth.user_id, userto = request.vars.recipient, msg = request.vars.msg)
    return "ok"


@auth.requires_login()
@auth.requires_signature()
def add_img_message():
    db.user_messages.insert(userfrom = auth.user_id, userto = request.vars.recipient, msg = None, img=db.images(request.vars.img))
    return "ok"


@auth.requires_login()
@auth.requires_signature()
def load_images():
    records = db(db.images.uploader == auth.user_id).select()
    d = {r.name: {'name': r.name, 'image': r.image, 'id': r.id} for r in records}
    return response.json(dict(images=d))

#TODO: make it so you can't be fluent in AND learning the same language
@auth.requires_login()
def reg_lang():
    """
    where user selects language preferences
    """
    auth.user = db.auth_user(auth.user_id)
    if auth.user.fluent is None or auth.user.learning is None:
        redirect(URL('default', 'init_user', user_signature=True))
    record = db.auth_user(auth.user_id).fluent
    form = SQLFORM(db.languages, record, formstyle='table3cols', showid=False)
    if form.process().accepted:
        #validates if form has at least one language checked
        if form.vars.Arabic | form.vars.Chinese | form.vars.Danish | form.vars.English |form.vars.French | form.vars.German | form.vars.Italian | form.vars.Japanese:
            #validates if user has chosen a language already learning
            if (form.vars.Arabic & auth.user.learning.Arabic) | (form.vars.Chinese & auth.user.learning.Chinese) | (form.vars.Danish & auth.user.learning.Danish) | (form.vars.English & auth.user.learning.English) | (form.vars.French & auth.user.learning.French) | (form.vars.German & auth.user.learning.German) | (form.vars.Italian & auth.user.learning.Italian) | (form.vars.Japanese & auth.user.learning.Japanese):
                response.flash = 'Cannot be fluent in language currently learning'
            else:
                if request.args(0) == 'settings':
                    redirect(URL('default', 'user', args='profile'))
                else:
                    redirect(URL('default', 'reg_lang2'))
        else:
            response.flash = 'Select a language to continue'
    return dict(form=form)


@auth.requires_login()
def reg_lang2():
    """
    where user selects language preferences
    """
    auth.user = db.auth_user(auth.user_id)
    if auth.user.fluent is None or auth.user.learning is None:
        redirect(URL('default', 'init_user', user_signature=True))
    record = db.auth_user(auth.user_id).learning
    form = SQLFORM(db.languages, record, formstyle='table3cols', showid=False)
    if form.process().accepted:
        #validates if form has at least one language checked
        if form.vars.Arabic | form.vars.Chinese | form.vars.Danish | form.vars.English |form.vars.French | form.vars.German | form.vars.Italian | form.vars.Japanese:
            #validates if user has chosen a language already fluent in
            if (form.vars.Arabic & auth.user.fluent.Arabic) | (form.vars.Chinese & auth.user.fluent.Chinese) | (form.vars.Danish & auth.user.fluent.Danish) | (form.vars.English & auth.user.fluent.English) | (form.vars.French & auth.user.fluent.French) | (form.vars.German & auth.user.fluent.German) | (form.vars.Italian & auth.user.fluent.Italian) | (form.vars.Japanese & auth.user.fluent.Japanese):
                response.flash = 'Cannot learn language already fluent in'
            else:
                #redirect conditions
                if request.args(0) == 'settings':
                    redirect(URL('default', 'user', args='profile'))
                else:
                    redirect(URL('default', 'index'))
        else:
            response.flash = 'Select a language to continue'
    return dict(form=form)


@auth.requires_login()
def home():
    """
    homepage
    """

    #matches users to other users who are fluent in a language you want to learn, and vice versa

    auth.user = db.auth_user(auth.user_id)
    if auth.user.fluent is None or auth.user.learning is None:
        redirect(URL('default', 'init_user', user_signature=True))
    # TODO: stretch goal, create a dynamic query that finds language table records that are fluent in the languages you want to learn
    # until then enjoy iterating over the entire user table every time
    # TODO: delete that comment before submitting
    user_table = db(db.auth_user.id > 0).select()
    matches = list()
    for record in user_table:
        match_to = list() #list of languages other users are fluent in that you want to learn
        match_from = list() # list of languages other users want to learn that you are fluent in
        match_flag = False
        if record.fluent.Arabic & auth.user.learning.Arabic:
            match_to.append('Arabic')
            match_flag = True
        if  record.fluent.Chinese & auth.user.learning.Chinese:
            match_to.append('Chinese')
            match_flag = True
        if  record.fluent.Danish & auth.user.learning.Danish:
            match_to.append('Danish')
            match_flag = True
        if  record.fluent.English & auth.user.learning.English:
            match_to.append('English')
            match_flag = True
        if  record.fluent.French & auth.user.learning.French:
            match_to.append('French')
            match_flag = True
        if  record.fluent.German & auth.user.learning.German:
            match_to.append('German')
            match_flag = True
        if  record.fluent.Italian & auth.user.learning.Italian:
            match_to.append('Italian')
            match_flag = True
        if  record.fluent.Japanese & auth.user.learning.Japanese:
            match_to.append('Japanese')
            match_flag = True
        if match_flag == True:
            match_flag = False
            if record.learning.Arabic & auth.user.fluent.Arabic:
                match_from.append('Arabic')
                match_flag = True
            if record.learning.Chinese & auth.user.fluent.Chinese:
                match_from.append('Chinese')
                match_flag = True
            if record.learning.Danish & auth.user.fluent.Danish:
                match_from.append('Danish')
                match_flag = True
            if record.learning.English & auth.user.fluent.English:
                match_from.append('English')
                match_flag = True
            if record.learning.French & auth.user.fluent.French:
                match_from.append('French')
                match_flag = True
            if record.learning.German & auth.user.fluent.German:
                match_from.append('German')
                match_flag = True
            if record.learning.Italian & auth.user.fluent.Italian:
                match_from.append('Italian')
                match_flag = True
            if record.learning.Japanese & auth.user.fluent.Japanese:
                match_from.append('Japanese')
                match_flag = True
            if match_flag == True:
                matches.append((record.screenname, match_to, match_from, record.id))

    return dict(matches=matches)

@auth.requires_login()
@auth.requires_signature()
def chat_win():
    """
    chat window
    """
    auth.user = db.auth_user(auth.user_id)
    if auth.user.fluent is None or auth.user.learning is None:
        redirect(URL('default', 'init_user', user_signature=True))
    return dict(messaging=request.args(0))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@auth.requires_login()
def gallery():
    records = db(db.images.uploader == auth.user_id).select()
    return dict(images=records)

def debug_user():
    return dict()


def reset():
    db.user_messages.truncate()
    return "Reset messages"


def reset_imgs():
    db.images.truncate()
    return "Reset images"


def reset_all():
    db.auth_user.truncate()
    db.languages.truncate()
    db.user_messages.truncate()
    return "Reset all"


@auth.requires_login()
def upload():
    form = SQLFORM(db.images)
    if form.process().accepted:
        redirect(URL('default', 'index'))
    return dict(form=form)

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
