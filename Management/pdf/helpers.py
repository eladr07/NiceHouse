from Management.templatetags.management_extras import commaise
from styles import *
from reportlab.platypus import Paragraph

class Row(list):
    def __init__(self, *args, **kw):
        super(Row, self).__init__(*args, **kw)
        self.height = None

class Col(object):
    __slots__ = ('name', 'title', 'width')
    
    def __init__(self, name, title, width):
        self.name, self.title, self.width = name, title, width

class FieldsGroup(object):
    def __init__(self, items, fields):
        self.items, self.fields = items, fields
    def reverse(self):
        self.fields.reverse()

class Table(object):
    def __init__(self, cols = None, rows = None):
        self.cols, self.rows = cols or [], rows or []
    def row_heights(self):
        return [row.height for row in self.rows]
    def col_widths(self):
        return [col.width for col in self.cols]
    def __len__(self):
        return self.rows.__len__()
    def __iter__(self):
        return self.rows.__iter__()

class Builder(object):
    def __init__(self, items, fields):
        self.items = items
        self.fields = fields
        
    def build(self, force_sum_row = False):
        row_summaries = dict([(field.name, 0) for field in self.fields if field.is_summarized])
        
        cols = [Col(field.name, field.title, field.width) for field in self.fields]
        
        if not cols:
            return Table()
        
        table = Table(cols = cols)
        
        title_row = Row([unicode(field.title) for field in self.fields])
        
        table.rows.append(title_row)
            
        for item in self.items:
            row = Row()
            
            for field in self.fields:
                cell_value = field.format(item)
                row.height = max(row.height, field.get_height(item))
                
                if field.is_summarized:
                    row_summaries[field.name] += cell_value
                    
                if field.is_commaised:
                    cell_value = commaise(cell_value)
    
                row.append(cell_value)
                
            table.rows.append(row)
        
        if row_summaries or force_sum_row:
            sum_row = Row()
            for field in self.fields:
                if field.is_summarized:
                    cell_value = Paragraph(commaise(row_summaries[field.name]), styleSumRow)
                    sum_row.append(cell_value)
                else:
                    sum_row.append('')
                    
            table.rows.append(sum_row)

        return table