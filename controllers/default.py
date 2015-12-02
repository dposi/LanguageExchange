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


#TODO: make it so you can't be fluent in AND learning the same language
@auth.requires_login()
def reg_lang():
    """
    where user selects language preferences
    """
    auth.user = db.auth_user(auth.user_id)
    if auth.user.fluent is None or auth.user.learning is None:
        redirect(URL('default', 'init_user'))
    record = db.auth_user(auth.user_id).fluent
    form = SQLFORM(db.languages, record, formstyle='table3cols', showid=False)
    if form.process().accepted:
        if request.args(0) == 'settings':
            redirect(URL('default', 'settings'))
        else:
            redirect(URL('default', 'reg_lang2'))
    return dict(form=form)


@auth.requires_login()
def reg_lang2():
    """
    where user selects language preferences
    """
    auth.user = db.auth_user(auth.user_id)
    if auth.user.fluent is None or auth.user.learning is None:
        redirect(URL('default', 'init_user'))
    record = db.auth_user(auth.user_id).learning
    form = SQLFORM(db.languages, record, formstyle='table3cols', showid=False)
    if form.process().accepted:
        if request.args(0) == 'settings':
            redirect(URL('default', 'settings'))
        else:
            redirect(URL('default', 'index'))
    return dict(form=form)


@auth.requires_login()
def home():
    """
    homepage
    """

    #matches users to other users who are fluent in a language you want to learn, and vice versa

    auth.user = db.auth_user(auth.user_id)
    if auth.user.fluent is None or auth.user.learning is None:
        redirect(URL('default', 'init_user'))
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
                matches.append((record.screenname, match_to, match_from))

    return dict(matches=matches)


@auth.requires_login()
def settings():
    """
    where user can change settings
    """
    return dict()

@auth.requires_login()
def chat_win():
    """
    chat window
    """
    return dict()


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


def cust_register():
    """
    customized registration
    """
    form = auth.register()
    if form.accepts(request,session):
        redirect(URL('reg_lang'))
    else:
        response.flash = 'Fill out details'
    return dict(form=form)


def debug_user():
    return dict()


def reset():
    db(db.auth_user.id > 0).delete()
    db(db.languages.id > 0).delete()
    db(db.messages.id > 0).delete()
    return dict()


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
