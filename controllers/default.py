# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

# ---- example index page ----
@auth.requires_membership('admin')
def index():
    grid = SQLFORM.grid(db.person,
                        links=[lambda r: A('Dossier bekijken', _href=URL('default', 'person', vars=dict(person=r.id)))])
    return dict(grid=grid)


@auth.requires_membership('admin')
def person():
    person_id = request.vars['person']
    if not person_id:
        return T("Oops! No person has been selected.")

    person = db(db.person.id == person_id).select().first()
    if not person:
        return T('Oops! This person doesn\'t exist (anymore).')

    form = SQLFORM(db.person, person)
    query = db.role_membership.person_id == person_id

    db.role_membership.person_id.default = person.id  # default value needs to be the id of the current dossier
    db.role_membership.person_id.writable = False  # setting this to False because we only want to edit records for this dossier

    # using constraints to execute a query with in a smartgrid, we're using this to only get the
    # role_membership records of this current person.
    # role_memberships = SQLFORM.smartgrid(db.role_membership, constraints=dict(role_membership=query),
    #                                      onvalidation=NO_ROLE_OVERLAP)
    role_memberships = SQLFORM.smartgrid(db.role_membership, constraints=dict(role_memberships=query),
                                         onvalidation=NO_MEMBERSHIP_OVERLAP)
    if form.process().accepted:
        response.flash = 'Wijzigingen opgeslagen.'

    return dict(person=person, form=form, role_memberships=role_memberships)


@auth.requires_membership('admin')
def roles():
    roles_smartgrid = SQLFORM.smartgrid(db.role)
    return dict(roles_smartgrid=roles_smartgrid)


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
