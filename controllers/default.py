# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

# ---- example index page ----
@auth.requires_membership('admin')
def index():
    grid = SQLFORM.grid(db.dossier,
                                  links=[lambda r: A('Dossier bekijken', _href=URL('default', 'dossier', vars=dict(
                                      dossier=r.id))) if 'view' in request.args or not request.vars[
                                      '_signature'] else ''])
    return dict(grid=grid)


@auth.requires_membership('admin')
def dossier():
    dossier_id = request.vars['dossier']
    if not dossier_id:
        return 'OEPS! er is geen dossier geselecteerd.'

    dossier = db(db.dossier.id == dossier_id).select().first()
    if not dossier:
        return 'OEPS! dit dossier bestaat niet (meer).'

    form = SQLFORM(db.dossier, dossier)
    query = db.dienstverband.dossier_id == dossier_id

    db.dienstverband.dossier_id.default = dossier.id  # default value needs to be the id of the current dossier
    db.dienstverband.dossier_id.writable = False  # setting this to False because we only want to edit records for this dossier

    # using constraints to execute a query with in a smartgrid, we're using this to only get the
    # dienstverband records of this current dossier.
    dienstverbanden = SQLFORM.smartgrid(db.dienstverband, constraints=dict(dienstverband=query),
                                        onvalidation=NO_ROLE_OVERLAP)
    if form.process().accepted:
        response.flash = 'Wijzigingen opgeslagen.'

    return dict(dossier=dossier, form=form, dienstverbanden=dienstverbanden)


@auth.requires_membership('admin')
def rollen():
    rollen_smartgrid = SQLFORM.smartgrid(db.rol)
    return dict(rollen_smartgrid=rollen_smartgrid)


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

# # ---- API (example) -----
# @auth.requires_login()
# def api_get_user_email():
#     if not request.env.request_method == 'GET': raise HTTP(403)
#     return response.json({'status': 'success', 'email': auth.user.email})
#
#
# # ---- Smart Grid (example) -----
# @auth.requires_membership('admin')  # can only be accessed by members of admin groupd
# def grid():
#     response.view = 'generic.html'  # use a generic view
#     tablename = request.args(0)
#     if not tablename in db.tables: raise HTTP(403)
#     grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
#     return dict(grid=grid)
#
#
# # ---- Embedded wiki (example) ----
# def wiki():
#     auth.wikimenu()  # add the wiki to the menu
#     return auth.wiki()
