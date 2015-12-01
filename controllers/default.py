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


#TODO: redirect here if language records for a user are None in case they get to the sign up page in a weird way
@auth.requires_login()
def init_user():
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
#TODO: redirect to init_user if the user's language records are None
@auth.requires_login()
def reg_lang():
    """
    where user selects language preferences
    """
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

    #finds one-way matches; ie users who are fluent in a language you want to learn
    fluent_table = db(
        db.languages.fluent == True
        ).select()
    owner_ids = list()
    for record in fluent_table:
        if (record.Arabic & auth.user.learning.Arabic |
            record.Chinese & auth.user.learning.Chinese |
            record.Danish & auth.user.learning.Danish |
            record.English & auth.user.learning.English |
            record.French & auth.user.learning.French |
            record.German & auth.user.learning.German |
            record.Italian & auth.user.learning.Italian |
            record.Japanese & auth.user.learning.Japanese):
                owner_ids.append(record.owner_id)

    #refines the list down to two-way matches; ie users who also want to learn a language you are fluent in
    double_matches = list()
    for owner_id in owner_ids:
        if owner_id != auth.user_id:
            owner = db.auth_user(owner_id)
            if (owner.learning.Arabic & auth.user.fluent.Arabic |
                owner.learning.Chinese & auth.user.fluent.Chinese |
                owner.learning.Danish & auth.user.fluent.Danish |
                owner.learning.English & auth.user.fluent.English |
                owner.learning.French & auth.user.fluent.French |
                owner.learning.German & auth.user.fluent.German |
                owner.learning.Italian & auth.user.fluent.Italian |
                owner.learning.Japanese & auth.user.fluent.Japanese):
                double_matches.append(owner.screenname)
    return dict(match_names=double_matches)


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
