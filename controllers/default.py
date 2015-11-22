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
def reg_lang():
    """
    where user selects language preferences
    """
    record = db.auth_user(auth.user_id).fluent
    form = SQLFORM(db.languages, record, formstyle='table3cols')
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
    form = SQLFORM(db.languages, record, formstyle='table3cols')
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
    return dict()

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


@auth.requires_login()
def debug_user():
    u = db.auth_user(auth.user_id)
    f = u.fluent
    l = u.learning
    return dict(f=f, l=l)


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
