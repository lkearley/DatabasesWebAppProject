from flask_table import Table, Col, LinkCol

class visitorHomeTable(Table):
    ID = Col('Id')
    Name = Col('Name')
    Street = Col('Street Address')
    City = Col('City')
    Zip = Col('Zip')
    State = Col('State')
    Type = Col('Type')
    IsPublic = Col('Public')
    IsCommercial = Col('Commercial')
    Visits = Col('Visits')
    allow_sort = True
    def sort_url(self, col_key, reverse=False):
        if reverse:
            direction =  'desc'
        else:
            direction = 'asc'
        return url_for('index', sort=col_key, direction=direction)

class PropertyTable(Table):
    Name = Col('Name')
    Street = Col('Street')
    City = Col('City')
    Zip = Col('Zip')
    Size = Col('Size')
    PropertyType = Col('Type')
    IsPublic = Col('Public')
    IsCommercial = Col('Commercial')
    ID = Col('ID')
    ApprovedBy = Col('Approved')
    edit = LinkCol('Manage', 'manageProperty', url_kwargs=dict(id='ID'))
    html_attrs = {'class': 'table table-bordered table-hover', 'style': "background-color: white"}

