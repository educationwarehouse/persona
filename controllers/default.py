# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

# ---- example index page ----
def index():
    response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))

@auth.requires_membership('admin')
def dossier():
    dossier_id = request.vars['id']
    if not dossier_id:
        return 'OEPS! er is iets fout gegaan.'
    dossier = db.dossier[dossier_id]
    form = SQLFORM(db.dossier, dossier)
    query = db.dienstverband.dossier_id == dossier_id
    # using constraints to execute a query with in a smartgrid, we're using this to only get the
    # dienstverband records of this current dossier.
    dienstverbanden = SQLFORM.smartgrid(db.dienstverband, constraints=dict(dienstverband=query))
    if form.process().accepted:
        response.flash = 'Wijzigingen opgeslagen.'
    return dict(dossier=dossier, form=form, dienstverbanden=dienstverbanden)

# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki() 

# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
